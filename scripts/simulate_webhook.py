"""
Send a fake but correctly-signed payment.dispute.created webhook to your
local FastAPI server, so the full pipeline (scoring + evidence drafting +
DB save) can be tested end-to-end without a real Razorpay account.

Usage:
    1. Start your FastAPI server in one terminal:
         uvicorn chargeguard.api.main:app --reload
    2. In another terminal, run this script:
         python scripts\\simulate_webhook.py
       Optionally override the defaults for demo scenarios:
         python scripts\\simulate_webhook.py --id disp_demo_low --reason credit_not_processed --amount 250000 --method credit_card
         python scripts\\simulate_webhook.py --id disp_demo_high --reason product_not_received --amount 899900 --method upi

Note: this call now runs the full pipeline (win-probability scoring +
Ollama letter drafting), so it will take longer than the earlier test --
expect anywhere from several seconds to a couple minutes depending on
your machine.
"""

import argparse
import hashlib
import hmac
import json
import os
import time

import requests

WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "test_webhook_secret")
TARGET_URL = "http://127.0.0.1:8000/webhooks/razorpay"


def build_payload(dispute_id: str, payment_id: str, amount_paise: int, reason_code: str, method: str) -> dict:
    return {
        "event": "payment.dispute.created",
        "payload": {
            "dispute": {
                "entity": {
                    "id": dispute_id,
                    "payment_id": payment_id,
                    "amount": amount_paise,
                    "currency": "INR",
                    "reason_code": reason_code,
                    "status": "open",
                    "created_at": int(time.time()),
                }
            },
            "payment": {
                "entity": {
                    "id": payment_id,
                    "method": method,
                }
            },
        },
    }


def sign_payload(raw_body: bytes) -> str:
    return hmac.new(
        key=WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", default="disp_simulated_002", help="dispute id")
    parser.add_argument("--amount", type=int, default=459900, help="amount in paise")
    parser.add_argument("--reason", default="product_not_received", help="reason code")
    parser.add_argument("--method", default="upi", help="payment method")
    args = parser.parse_args()

    payment_id = args.id.replace("disp_", "pay_")
    payload = build_payload(args.id, payment_id, args.amount, args.reason, args.method)

    raw_body = json.dumps(payload).encode("utf-8")
    signature = sign_payload(raw_body)

    print("Sending simulated webhook to:", TARGET_URL)
    print(f"Dispute: {args.id} | reason: {args.reason} | amount: {args.amount/100:.2f} | method: {args.method}")
    print("(this now runs the full pipeline -- scoring + LLM letter drafting -- so it may take a bit)")

    response = requests.post(
        TARGET_URL,
        data=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
        },
    )

    print("\nStatus code:", response.status_code)
    print("Response body:")
    print(json.dumps(response.json(), indent=2))