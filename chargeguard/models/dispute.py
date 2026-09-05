from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from chargeguard.core.database import Base
from chargeguard.services.evidence_composer import retrieve_evidence, validate_letter

class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    razorpay_dispute_id = Column(String, unique=True, index=True)
    payment_id = Column(String, index=True)
    reason_code = Column(String)
    payment_method = Column(String, nullable=True)
    amount = Column(Float)
    status = Column(String, default="action_required")
    evidence_completeness = Column(Float, default=0.0)
    win_probability = Column(Float, nullable=True)
    evidence_letter = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())