"""
Typed Razorpay client for dispute-related operations.

Uses the official `razorpay` Python SDK under the hood. Reads credentials
from environment variables so no keys are ever hardcoded:

  RAZORPAY_KEY_ID
  RAZORPAY_KEY_SECRET

In test/dev mode without real credentials, these can be left unset --
the client will simply not be able to make live calls, but the rest of
the pipeline (webhook handling, evidence composition) works independently
via the simulated webhook script.
"""

import os
from dataclasses import dataclass
from typing import Any

import razorpay


@dataclass
class DisputeRecord:
    dispute_id: str
    payment_id: str
    amount: int  # paise, matching Razorpay's convention
    currency: str
    reason_code: str
    status: str
    created_at: int  # unix timestamp, matching Razorpay's convention


class RazorpayClient:
    def __init__(self, key_id: str | None = None, key_secret: str | None = None):
        key_id = key_id or os.environ.get("RAZORPAY_KEY_ID")
        key_secret = key_secret or os.environ.get("RAZORPAY_KEY_SECRET")

        if not key_id or not key_secret:
            self._client = None
            self._configured = False
        else:
            self._client = razorpay.Client(auth=(key_id, key_secret))
            self._configured = True

    @property
    def is_configured(self) -> bool:
        return self._configured

    def get_dispute(self, dispute_id: str) -> DisputeRecord:
        if not self._configured:
            raise RuntimeError(
                "RazorpayClient has no credentials configured. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to make live calls."
            )
        raw: dict[str, Any] = self._client.dispute.fetch(dispute_id)
        return DisputeRecord(
            dispute_id=raw["id"],
            payment_id=raw["payment_id"],
            amount=raw["amount"],
            currency=raw["currency"],
            reason_code=raw["reason_code"],
            status=raw["status"],
            created_at=raw["created_at"],
        )

    def submit_evidence(self, dispute_id: str, evidence_text: str, document_ids: list[str] | None = None) -> dict:
        if not self._configured:
            raise RuntimeError(
                "RazorpayClient has no credentials configured. "
                "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to make live calls."
            )
        payload: dict[str, Any] = {"summary": evidence_text}
        if document_ids:
            payload["document_ids"] = document_ids
        return self._client.dispute.submit_evidence(dispute_id, payload)