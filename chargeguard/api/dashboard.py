"""
Dashboard API endpoints.

These are new, thin HTTP wrappers around existing service functions
(ml/scoring.py, services/evidence_composer.py, the Dispute model) so a
separate frontend (e.g. Next.js) can consume them over REST. No ML, RAG,
or webhook logic is changed here -- this file only reads and re-shapes
data that already exists.
"""

import json
import os

import joblib
import shap
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from chargeguard.core.database import get_db
from chargeguard.models.dispute import Dispute
from chargeguard.ml.scoring import build_feature_vector
from chargeguard.services.evidence_composer import retrieve_evidence, validate_letter

router = APIRouter(prefix="/api", tags=["dashboard"])

_shap_cache = {}


def _get_shap_explainer():
    if "explainer" not in _shap_cache:
        raw_model = joblib.load("models/win_model_raw.pkl")
        feature_columns = joblib.load("models/feature_columns.pkl")
        _shap_cache["explainer"] = shap.Explainer(raw_model)
        _shap_cache["feature_columns"] = feature_columns
    return _shap_cache["feature_columns"], _shap_cache["explainer"]


def _dispute_to_dict(d: Dispute) -> dict:
    return {
        "razorpay_dispute_id": d.razorpay_dispute_id,
        "payment_id": d.payment_id,
        "reason_code": d.reason_code,
        "payment_method": d.payment_method,
        "amount": d.amount,
        "status": d.status,
        "evidence_completeness": d.evidence_completeness,
        "win_probability": d.win_probability,
        "evidence_letter": d.evidence_letter,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


@router.get("/disputes")
def list_disputes(db: Session = Depends(get_db)):
    rows = db.query(Dispute).order_by(Dispute.created_at.desc()).all()
    return [_dispute_to_dict(r) for r in rows]


@router.get("/disputes/{dispute_id}")
def get_dispute(dispute_id: str, db: Session = Depends(get_db)):
    row = db.query(Dispute).filter(Dispute.razorpay_dispute_id == dispute_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Dispute not found")

    data = _dispute_to_dict(row)

    evidence_items = retrieve_evidence(row.reason_code) if row.reason_code else []
    data["evidence_items"] = evidence_items

    validation = validate_letter(row.evidence_letter or "", evidence_items)
    data["validation"] = validation

    return data


@router.get("/disputes/{dispute_id}/shap")
def get_dispute_shap(dispute_id: str, db: Session = Depends(get_db)):
    row = db.query(Dispute).filter(Dispute.razorpay_dispute_id == dispute_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Dispute not found")

    feature_columns, explainer = _get_shap_explainer()

    feature_row = build_feature_vector(
        reason_code=row.reason_code,
        payment_method=row.payment_method,
        amount=row.amount,
        created_at=row.created_at,
        evidence_completeness=row.evidence_completeness or 0.5,
    )

    explanation = explainer(feature_row)
    values = explanation.values[0]

    contributions = sorted(
        [{"feature": f, "shap_value": float(v)} for f, v in zip(feature_columns, values)],
        key=lambda x: abs(x["shap_value"]),
        reverse=True,
    )[:10]

    return {"dispute_id": dispute_id, "contributions": contributions}


@router.get("/model/metrics")
def get_model_metrics():
    path = "models/metrics.json"
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found. Run scripts/train_model.py first.",
        )
    with open(path) as f:
        return json.load(f)