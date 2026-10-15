import os
import uuid
import time
import json
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.features import extract_features
from app.database import SessionLocal, ScanRecord

app = FastAPI(title="PhishGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "phishguard_rf.joblib")
model = None

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        print("Warning: Model file not found. Run train_model.py first.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AnalyzeRequest(BaseModel):
    url: str

@app.post("/api/v1/analyze")
def analyze_url(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    url = payload.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    extracted = extract_features(url)
    vector = np.array(extracted["vector"]).reshape(1, -1)

    if model:
        proba = model.predict_proba(vector)[0][1]
        risk_score = int(round(proba * 100))
    else:
        risk_score = 75 if len(extracted["signals"]) >= 2 else 20

    if risk_score >= 70:
        classification = "Phishing"
    elif risk_score >= 40:
        classification = "Suspicious"
    else:
        classification = "Safe"

    scan_id = str(uuid.uuid4())
    duration_ms = round((time.time() - start_time) * 1000, 2)

    record = ScanRecord(
        id=scan_id,
        url=url,
        classification=classification,
        risk_score=risk_score,
        signals=json.dumps(extracted["signals"])
    )
    db.add(record)
    db.commit()

    return {
        "scan_id": scan_id,
        "url": url,
        "classification": classification,
        "risk_score": risk_score,
        "signals": extracted["signals"],
        "feature_summary": extracted["feature_summary"],
        "processing_time_ms": duration_ms
    }

@app.get("/api/v1/history")
def get_history(db: Session = Depends(get_db)):
    scans = db.query(ScanRecord).order_by(ScanRecord.created_at.desc()).limit(15).all()
    return [
        {
            "id": s.id,
            "url": s.url,
            "classification": s.classification,
            "risk_score": s.risk_score,
            "signals": json.loads(s.signals),
            "created_at": s.created_at.isoformat()
        }
        for s in scans
    ]

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}
