"""
Feature engineering for ChargeGuard win-probability model.

Reads data/disputes.json, builds a model-ready feature matrix, and
writes it to data/features.csv.

Encoding decisions:
  - reason_code, payment_method  -> one-hot encoded (interpretable, small cardinality)
  - created_at                   -> month + day_of_week, both cyclically encoded (sin/cos)
                                     so e.g. December (12) and January (1) are close in
                                     feature space instead of maximally far apart
  - festival_season               -> kept as 0/1
  - evidence_completeness, amount -> kept as-is (already numeric, sensible ranges)
  - id columns, raw created_at    -> dropped (not model inputs)
"""

import json
import math

import pandas as pd


def add_cyclical_features(df: pd.DataFrame, col: str, period: int) -> pd.DataFrame:
    """Replace an integer column with sin/cos pairs on the given period."""
    radians = 2 * math.pi * df[col] / period
    df[f"{col}_sin"] = radians.apply(math.sin).round(6)
    df[f"{col}_cos"] = radians.apply(math.cos).round(6)
    return df.drop(columns=[col])


def build_features(raw_path: str = "data/disputes.json") -> pd.DataFrame:
    with open(raw_path) as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # created_at was serialized to string via default=str in generate_data.py
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["month"] = df["created_at"].dt.month
    df["day_of_week"] = df["created_at"].dt.dayofweek  # 0=Monday

    df = add_cyclical_features(df, "month", period=12)
    df = add_cyclical_features(df, "day_of_week", period=7)

    df["festival_season"] = df["festival_season"].astype(int)

    df = pd.get_dummies(
        df,
        columns=["reason_code", "payment_method"],
        prefix=["reason", "pay"],
    )

    # convert one-hot bools to 0/1 ints for a cleaner CSV / model input
    onehot_cols = [c for c in df.columns if c.startswith("reason_") or c.startswith("pay_")]
    df[onehot_cols] = df[onehot_cols].astype(int)

    df["won"] = df["won"].astype(int)

    id_cols = ["razorpay_dispute_id", "payment_id", "created_at"]
    df = df.drop(columns=id_cols)

    return df


if __name__ == "__main__":
    features = build_features()
    features.to_csv("data/features.csv", index=False)

    print("=== Feature matrix shape ===")
    print(features.shape)

    print("\n=== Columns ===")
    for c in features.columns:
        print(" -", c)

    print("\n=== Sample rows ===")
    print(features.head(3).to_string())

    print("\n=== Class balance (won) ===")
    print(features["won"].value_counts(normalize=True).round(3))

    print("\nSaved -> data/features.csv")