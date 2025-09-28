import os
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from typing import Dict, Any
from .database import SessionLocal
from . import models

MODEL_DIR = os.environ.get("MODEL_DIR", "./models")
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(MODEL_DIR, "dropout_model.pkl"))
os.makedirs(MODEL_DIR, exist_ok=True)

def fetch_training_data() -> pd.DataFrame:
    db: Session = SessionLocal()
    try:
        q = db.query(models.Student).filter(models.Student.drop_out != None).all()
        rows = []
        for r in q:
            rows.append({
                "student_id": r.student_id,
                "age": r.age,
                "gender": r.gender,
                "attendance_percentage": r.attendance_percentage,
                "gpa": r.gpa,
                "parent_education": r.parent_education,
                "socioeconomic_status": r.socioeconomic_status,
                "extracurricular_participation": r.extracurricular_participation,
                "previous_failures": r.previous_failures,
                "drop_out": r.drop_out
            })
        df = pd.DataFrame(rows)
        return df
    finally:
        db.close()

def train_and_save_model(params: Dict[str, Any] = None):
    params = params or {}
    df = fetch_training_data()
    if df.empty or len(df) < 50:
        print("Not enough labelled rows to train. Need at least ~50 labelled examples.")
        return {"status": "not_enough_data", "n": len(df)}
    features = [
        "student_id", "age", "gender", "attendance_percentage", "gpa",
        "parent_education", "socioeconomic_status", "extracurricular_participation",
        "previous_failures"
    ]
    X = df[features].copy()
    y = df["drop_out"]
    X = pd.get_dummies(X, drop_first=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=params.get("test_size", 0.2), random_state=42
    )
    pipeline = Pipeline([("clf", LogisticRegression(max_iter=params.get("max_iter", 1000)))])
    pipeline.fit(X_train, y_train)
    trained_features = X.columns.tolist()
    joblib.dump((pipeline, trained_features), MODEL_PATH)
    print(f"Model trained and saved: {MODEL_PATH}")
    db = SessionLocal()
    try:
        m = models.ModelArtifact(name=params.get("model_name", "dropout-model"), path=MODEL_PATH, metadata_json={})
        db.add(m)
        db.commit()
        db.refresh(m)
        run = models.TrainingRun(model_id=m.id, params=params, metrics={"train_n": len(X_train), "test_n": len(X_test)})
        db.add(run)
        db.commit()
    finally:
        db.close()
    return {"status":"trained","model_path":MODEL_PATH}
