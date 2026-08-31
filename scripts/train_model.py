"""
Train the ChargeGuard win-probability model.

Pipeline:
  1. Load data/features.csv
  2. Stratified 80/20 train/holdout split
  3. Train an XGBoost classifier on the train split
  4. Calibrate probabilities with Platt scaling (sigmoid) using
     CalibratedClassifierCV, fit on the train split via internal CV
  5. Evaluate on the untouched holdout set: ROC AUC, Brier score, reliability table
  6. Save the calibrated model to models/win_model.pkl (used for actual
     win-probability predictions shown to users)
  7. Also save the raw, uncalibrated base model to models/win_model_raw.pkl
     -- this is used ONLY for SHAP explainability, since the calibrated
     model is a 5-fold ensemble with no single clean decision path for
     SHAP to explain. Same features, same tree structure; just used for
     "why" rather than "what probability."
  8. Save summary metrics (AUC, Brier, holdout size, reliability table) to
     models/metrics.json so the dashboard can display them without needing
     to re-run training.
"""

import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


def load_data(path: str = "data/features.csv"):
    df = pd.read_csv(path)
    y = df["won"]
    X = df.drop(columns=["won"])
    return X, y


def reliability_table(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    bins = pd.cut(y_prob, bins=np.linspace(0, 1, n_bins + 1), include_lowest=True)
    table = pd.DataFrame({"bucket": bins, "y_true": y_true, "y_prob": y_prob})
    summary = table.groupby("bucket", observed=True).agg(
        n=("y_true", "size"),
        actual_win_rate=("y_true", "mean"),
        avg_predicted_prob=("y_prob", "mean"),
    )
    return summary.round(3)


def main():
    X, y = load_data()

    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("=== Split sizes ===")
    print(f"Train: {X_train.shape}, Holdout: {X_holdout.shape}")

    base_model = XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
    )

    print("\nTraining base XGBoost model...")
    base_model.fit(X_train, y_train)

    raw_probs = base_model.predict_proba(X_holdout)[:, 1]
    raw_auc = roc_auc_score(y_holdout, raw_probs)
    raw_brier = brier_score_loss(y_holdout, raw_probs)
    print("\n=== Raw (uncalibrated) model ===")
    print(f"AUC:   {raw_auc:.4f}")
    print(f"Brier: {raw_brier:.4f}")

    print("\nCalibrating with Platt scaling (sigmoid), 5-fold internal CV on train set...")
    calibrated_model = CalibratedClassifierCV(base_model, method="sigmoid", cv=5)
    calibrated_model.fit(X_train, y_train)

    cal_probs = calibrated_model.predict_proba(X_holdout)[:, 1]
    cal_auc = roc_auc_score(y_holdout, cal_probs)
    cal_brier = brier_score_loss(y_holdout, cal_probs)
    print("\n=== Calibrated model (holdout) ===")
    print(f"AUC:   {cal_auc:.4f}")
    print(f"Brier: {cal_brier:.4f}")

    reliability = reliability_table(y_holdout.to_numpy(), cal_probs)
    print("\n=== Reliability table (calibrated) ===")
    print(reliability)

    print("\n=== Top 10 feature importances (from base XGBoost model) ===")
    importances = pd.Series(base_model.feature_importances_, index=X_train.columns)
    top_importances = importances.sort_values(ascending=False).head(10).round(4)
    print(top_importances)

    os.makedirs("models", exist_ok=True)
    joblib.dump(calibrated_model, "models/win_model.pkl")
    joblib.dump(base_model, "models/win_model_raw.pkl")
    joblib.dump(list(X.columns), "models/feature_columns.pkl")
    print("\nSaved calibrated model -> models/win_model.pkl")
    print("Saved raw model (for SHAP) -> models/win_model_raw.pkl")
    print("Saved feature column order -> models/feature_columns.pkl")

    # --- Save summary metrics for dashboard display ---
    metrics = {
        "train_size": int(X_train.shape[0]),
        "holdout_size": int(X_holdout.shape[0]),
        "raw_model": {
            "auc": round(float(raw_auc), 4),
            "brier_score": round(float(raw_brier), 4),
        },
        "calibrated_model": {
            "auc": round(float(cal_auc), 4),
            "brier_score": round(float(cal_brier), 4),
        },
        "reliability_table": [
            {
                "bucket": str(idx),
                "n": int(r["n"]),
                "actual_win_rate": float(r["actual_win_rate"]),
                "avg_predicted_prob": float(r["avg_predicted_prob"]),
            }
            for idx, r in reliability.iterrows()
        ],
        "top_feature_importances": [
            {"feature": name, "importance": float(val)}
            for name, val in top_importances.items()
        ],
    }

    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Saved summary metrics -> models/metrics.json")


if __name__ == "__main__":
    main()