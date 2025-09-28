import os
import joblib
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import pandas as pd
from .database import SessionLocal, engine, Base
from . import models, schemas
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Live Ingestion + Model API")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/health")
def health():
    return {"status":"ok"}
@app.post("/ingest/students", response_model=dict)
def ingest_students(payload: schemas.StudentBatch, db: Session = Depends(get_db)):
    inserted = 0
    for s in payload.students:
        if s.student_id is not None:
            existing = db.query(models.Student).filter(models.Student.student_id == s.student_id).first()
        else:
            existing = None
        if existing:
            for k, v in s.dict().items():
                if v is not None and k != "student_id":
                    setattr(existing, k, v)
            db.add(existing)
        else:
            new = models.Student(**s.dict())
            db.add(new)
        inserted += 1
    db.commit()
    return {"ingested": inserted}
from .train_model import train_and_save_model
@app.post("/train", response_model=dict)
def train_endpoint(req: schemas.TrainRequest = None, background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
    # run in background if background_tasks provided (FastAPI will supply when invoked via HTTP)
    params = req.dict() if req else {}
    if background_tasks:
        background_tasks.add_task(train_and_save_model, params)
        return {"status":"training_started"}
    # else run sync
    result = train_and_save_model(params)
    return result
@app.post("/predict", response_model=dict)
def predict(req: schemas.PredictRequest, db: Session = Depends(get_db)):
    model_path = os.environ.get("MODEL_PATH", "./models/dropout_model.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="Model artifact not found. Train first.")
    model, trained_features = joblib.load(model_path)
    df = pd.DataFrame([s.dict() for s in req.students])
    X_new = df.copy()
    X_new = pd.get_dummies(X_new, drop_first=True)
    for col in trained_features:
        if col not in X_new.columns:
            X_new[col] = 0
    X_new = X_new[trained_features]
    preds = model.predict(X_new)
    probs = model.predict_proba(X_new)[:,1] if hasattr(model, "predict_proba") else [None]*len(preds)
    results = []
    for i, row in df.iterrows():
        student_raw_id = row.get("student_id", None)
        student_row = None
        if student_raw_id is not None:
            student_row = db.query(models.Student).filter(models.Student.student_id == student_raw_id).first()
        pred = models.Prediction(
            student_id = student_row.id if student_row else None,
            raw_student_id = student_raw_id,
            predicted_label = int(preds[i]),
            probability = float(probs[i]) if probs is not None else None,
            model_id = None
        )
        db.add(pred)
        results.append({
            "student_id": student_raw_id,
            "predicted_label": int(preds[i]),
            "probability": float(probs[i]) if probs is not None else None
        })
    db.commit()
    return {"predictions": results}
