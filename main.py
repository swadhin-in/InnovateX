# main.py - entrypoint to run API, auto-trainer, and optional bulk import
import os
import time
import threading
import signal
import logging
from datetime import datetime, timezone
import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn

from backend.api import app
from backend.train_model import train_and_save_model
from backend.database import SessionLocal, Base, engine
from backend import models as dbmodels
from sqlalchemy.orm import Session
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")

def bulk_load_csv_to_students(csv_path: str) -> int:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    df = pd.read_csv(csv_path)
    processed = 0
    db: Session = SessionLocal()
    try:
        for _, row in df.iterrows():
            payload = row.to_dict()
            sid = payload.get("student_id", None)
            if sid is not None:
                existing = db.query(dbmodels.Student).filter(dbmodels.Student.student_id == int(sid)).first()
            else:
                existing = None
            allowed = { "student_id","age","gender","attendance_percentage","gpa","parent_education","socioeconomic_status","extracurricular_participation","previous_failures","drop_out" }
            data = {k: (None if pd.isna(v) else v) for k,v in payload.items() if k in allowed}
            if existing:
                for k,v in data.items():
                    setattr(existing, k, v)
                db.add(existing)
            else:
                new = dbmodels.Student(**data)
                db.add(new)
            processed += 1
        db.commit()
    finally:
        db.close()
    logger.info(f"Bulk loaded {processed} rows from {csv_path}")
    return processed

def _api_runner(host: str, port: int):
    uvicorn.run(app, host=host, port=port, log_level="info", access_log=False)

def start_api_in_thread(host: str='127.0.0.1', port: int=8000):
    t = threading.Thread(target=_api_runner, args=(host,port), daemon=True, name='uvicorn-thread')
    t.start()
    logger.info("FastAPI started in background")
    return t

def get_last_training_time(db: Session):
    latest = db.query(dbmodels.TrainingRun).order_by(dbmodels.TrainingRun.finished_at.desc().nulls_last()).first()
    if latest and latest.finished_at:
        return latest.finished_at
    if latest and latest.started_at:
        return latest.started_at
    return None

def count_labeled_since(db: Session, since):
    q = db.query(func.count(dbmodels.Student.id)).filter(dbmodels.Student.drop_out != None)
    if since:
        q = q.filter(dbmodels.Student.created_at > since)
    return int(q.scalar() or 0)

def trigger_train(params=None):
    params = params or {}
    logger.info("Triggering training with params: %s", params)
    try:
        res = train_and_save_model(params)
        logger.info("Training finished: %s", res)
        return {"status":"ok","result":res}
    except Exception as e:
        logger.exception("Training failed")
        return {"status":"error","error":str(e)}

class AutoTrainer:
    def __init__(self, interval_min=60, labeled_threshold=50):
        self.interval_min = interval_min
        self.labeled_threshold = labeled_threshold
        self.scheduler = BackgroundScheduler()
    def start(self):
        self.scheduler.add_job(self.check_and_train, 'interval', minutes=self.interval_min, next_run_time=datetime.now())
        self.scheduler.start()
        logger.info("AutoTrainer started")
    def check_and_train(self):
        db = SessionLocal()
        try:
            last = get_last_training_time(db)
            labeled_new = count_labeled_since(db, last)
            logger.info("Found %d new labeled rows since last train (%s)", labeled_new, last)
            if labeled_new >= self.labeled_threshold:
                trigger_train({"test_size":0.2})
        finally:
            db.close()
    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("AutoTrainer stopped")

def main(bulk_csv=None, host='127.0.0.1', port=8000, interval_min=60, threshold=50, run_initial=False):
    init_db()
    if bulk_csv:
        try:
            bulk_load_csv_to_students(bulk_csv)
        except Exception as e:
            logger.exception("Bulk load failed: %s", e)
    api_thread = start_api_in_thread(host, port)
    trainer = AutoTrainer(interval_min, threshold)
    trainer.start()
    if run_initial:
        db = SessionLocal()
        try:
            last = get_last_training_time(db)
            labeled = count_labeled_since(db, last)
            if labeled >= 10:
                trigger_train({"test_size":0.2})
        finally:
            db.close()
    def _signal(sig, frame):
        logger.info("Shutting down...")
        try:
            trainer.stop()
        except:
            pass
        raise SystemExit()
    signal.signal(signal.SIGINT, _signal)
    signal.signal(signal.SIGTERM, _signal)
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        trainer.stop()
        logger.info("Exited")

if __name__ == "__main__":
    bulk = os.environ.get("BULK_CSV_PATH")
    interval = int(os.environ.get("AUTO_TRAIN_INTERVAL_MIN","60"))
    threshold = int(os.environ.get("AUTO_TRAIN_THRESHOLD","50"))
    run_init = os.environ.get("RUN_INITIAL_TRAIN","0") == "1"
    host = os.environ.get("HOST","127.0.0.1")
    port = int(os.environ.get("PORT","8000"))
    main(bulk_csv=bulk, host=host, port=port, interval_min=interval, threshold=threshold, run_initial=run_init)
