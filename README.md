# Dropout Prediction Model — Live DB-enabled Repo

This repository contains a backend FastAPI application and ML training pipeline
that uses a live SQL database (SQLite by default) for ingestion, training and prediction.

## Quick start (local)

1. Create virtualenv and activate:
```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\activate
# bash
source .venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Start the whole app (API + auto-trainer):
```bash
python main.py
```

4. API:
- Health: `GET http://127.0.0.1:8000/health`
- Ingest students: `POST /ingest/students`
- Trigger training (background): `POST /train`
- Predict: `POST /predict`

## Files
- `main.py` — single entrypoint (starts FastAPI and background auto-trainer).
- `backend/` — FastAPI app and ML training code.
- `scripts/` — helper scripts to generate dummy data and call endpoints.

## Notes
- Default DB: `sqlite:///./app.db` (file `app.db` created at repo root).
- Models are saved to `./models/` directory.
