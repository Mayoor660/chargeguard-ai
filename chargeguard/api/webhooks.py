"""
Webhook handler for Razorpay dispute events.

On payment.dispute.created:
  1. Verify webhook signature
  2. Parse dispute details
  3. Score a preliminary win probability using a neutral evidence-completeness
     baseline (0.5), since no evidence has been gathered yet at this point
  4. Retrieve relevant evidence + draft a representment letter via the local
     Ollama-backed composer
  5. Persist everything to the disputes table

Note: steps 3-4 run synchronously inside the request for simplicity in this
demo. In a production system these would be offloaded to a background task
queue so the webhook can return immediately (Razorpay expects a fast 200).
"""

import hashlib
import hmac
import os
from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, Request

from chargeguard.core.database import SessionLocal
from chargeguard.models.dispute import Dispute
from chargeguard.ml.scoring import predict_win_probability
from chargeguard.services.evidence_composer import compose_letter

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "test_webhook_secret")

BASELINE_EVIDENCE_COMPLETENESS = 0.5  # neutral; real value unknown at intake time


def verify_signature(raw_body: bytes, signature: str) -> bool:
    expected = hmac.new(
        key=WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(default=""),
):
    raw_body = await request.body()

    if not verify_signature(raw_body, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event")

    if event != "payment.dispute.created":
        return {"status": "ignored", "event": event}

    dispute_entity = payload["payload"]["dispute"]["entity"]
    payment_entity = payload["payload"].get("payment", {}).get("entity", {})

    reason_code = dispute_entity["reason_code"]
    payment_method = payment_entity.get("method", "upi")  # fallback if not present
    amount = dispute_entity["amount"] / 100  # paise -> rupees
    created_at = datetime.fromtimestamp(dispute_entity["created_at"])

    win_probability = predict_win_probability(
        reason_code=reason_code,
        payment_method=payment_method,
        amount=amount,
        created_at=created_at,
        evidence_completeness=BASELINE_EVIDENCE_COMPLETENESS,
    )

    composed = compose_letter(
    reason_code=reason_code,
    amount=amount,
    payment_method=payment_method,
    dispute_date=created_at.strftime("%B %d, %Y"),
    tracking_ref=f"TRK-{dispute_entity['id'].upper()}",
)

    db = SessionLocal()
    try:
        existing = (
            db.query(Dispute)
            .filter(Dispute.razorpay_dispute_id == dispute_entity["id"])
            .first()
        )
        if existing:
            db_dispute = existing
        else:
            db_dispute = Dispute(razorpay_dispute_id=dispute_entity["id"])

        db_dispute.payment_id = dispute_entity["payment_id"]
        db_dispute.reason_code = reason_code
        db_dispute.payment_method = payment_method
        db_dispute.amount = amount
        db_dispute.status = dispute_entity.get("status", "action_required")
        db_dispute.evidence_completeness = BASELINE_EVIDENCE_COMPLETENESS
        db_dispute.win_probability = win_probability
        db_dispute.evidence_letter = composed["letter"]

        db.add(db_dispute)
        db.commit()
        db.refresh(db_dispute)
    finally:
        db.close()

    return {
        "status": "processed",
        "dispute_id": dispute_entity["id"],
        "win_probability": win_probability,
        "letter_word_count": composed["validation"]["word_count"],
        "letter_validation_passed": composed["validation"]["passed"],
        "evidence_types_used": [e["evidence_type"] for e in composed["evidence_used"]],
    }