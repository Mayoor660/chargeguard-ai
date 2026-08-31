"""
Win-probability scoring for live disputes.

Loads the calibrated XGBoost model trained in scripts/train_model.py and
scores a single incoming dispute, building a feature vector that matches
the exact column order the model was trained on.

IMPORTANT: at webhook-receipt time, no evidence has been gathered yet, so
evidence_completeness is unknown. Callers should pass a neutral baseline
(0.5) for a preliminary score, then re-score later once real evidence
completeness can be assessed (e.g. after evidence review). Passing a
fabricated non-neutral value here would produce a falsely precise number.
"""

import math
from datetime import datetime

import joblib
import pandas as pd

MODEL_PATH = "models/win_model.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"

_model = None
_feature_columns = None


def _load():
    global _model, _feature_columns
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
    return _model, _feature_columns


def _cyclical(value: int, period: int) -> tuple[float, float]:
    radians = 2 * math.pi * value / period
    return round(math.sin(radians), 6), round(math.cos(radians), 6)


def build_feature_vector(
    reason_code: str,
    payment_method: str,
    amount: float,
    created_at: datetime,
    evidence_completeness: float,
) -> pd.DataFrame:
    model, feature_columns = _load()

    row = {col: 0 for col in feature_columns}

    row["amount"] = amount
    row["evidence_completeness"] = evidence_completeness
    row["festival_season"] = 1 if created_at.month in (10, 11) else 0

    month_sin, month_cos = _cyclical(created_at.month, 12)
    dow_sin, dow_cos = _cyclical(created_at.weekday(), 7)
    row["month_sin"] = month_sin
    row["month_cos"] = month_cos
    row["day_of_week_sin"] = dow_sin
    row["day_of_week_cos"] = dow_cos

    reason_col = f"reason_{reason_code}"
    if reason_col in row:
        row[reason_col] = 1

    pay_col = f"pay_{payment_method}"
    if pay_col in row:
        row[pay_col] = 1

    return pd.DataFrame([row], columns=feature_columns)


def predict_win_probability(
    reason_code: str,
    payment_method: str,
    amount: float,
    created_at: datetime,
    evidence_completeness: float = 0.5,
) -> float:
    model, _ = _load()
    X = build_feature_vector(reason_code, payment_method, amount, created_at, evidence_completeness)
    prob = model.predict_proba(X)[:, 1][0]
    return round(float(prob), 4)