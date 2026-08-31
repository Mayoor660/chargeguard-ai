import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible synthetic data

REASON_CODES = [
    "fraudulent", "product_not_received", "product_unacceptable",
    "duplicate_processing", "credit_not_processed", "subscription_canceled",
    "unrecognized", "processed_invalid_expired_card",
]

PAYMENT_METHODS = ["upi", "credit_card", "debit_card", "netbanking", "wallet"]
PAYMENT_WEIGHTS = [0.42, 0.20, 0.18, 0.12, 0.08]  # rough Indian payment mix


def is_festival_season(dt: datetime) -> bool:
    return dt.month in (10, 11)  # Oct-Nov: festival shopping season


def generate_dispute(i: int):
    created_at = datetime.now() - timedelta(days=random.randint(0, 365))
    festival = is_festival_season(created_at)

    # festival season skews toward product_not_received (shipping delays, order surges)
    if festival and random.random() < 0.4:
        reason = "product_not_received"
    else:
        reason = random.choice(REASON_CODES)

    payment_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]
    evidence_completeness = round(random.uniform(0.1, 1.0), 2)

    base_win_prob = 0.2 + (evidence_completeness * 0.6)
    noise = random.uniform(-0.15, 0.15)
    true_win_prob = max(0.0, min(1.0, base_win_prob + noise))
    won = random.random() < true_win_prob

    amount = round(random.uniform(200, 15000), 2)
    if festival:
        amount = round(amount * random.uniform(1.1, 1.4), 2)

    return {
        "razorpay_dispute_id": f"disp_{i:06d}",
        "payment_id": f"pay_{i:06d}",
        "reason_code": reason,
        "payment_method": payment_method,
        "amount": amount,
        "evidence_completeness": evidence_completeness,
        "won": won,
        "festival_season": festival,
        "created_at": created_at,
    }


def generate_dataset(n=50000):
    return [generate_dispute(i) for i in range(n)]


if __name__ == "__main__":
    import json
    data = generate_dataset(50000)
    with open("data/disputes.json", "w") as f:
        json.dump(data, f, default=str, indent=2)
    print(f"Generated {len(data)} synthetic disputes -> data/disputes.json")