import json
import pandas as pd

with open("data/disputes.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

print("=== Shape ===")
print(df.shape)

print("\n=== Reason code distribution ===")
print(df["reason_code"].value_counts())

print("\n=== Payment method distribution ===")
print(df["payment_method"].value_counts(normalize=True).round(3))

print("\n=== Overall win rate ===")
print(df["won"].mean().round(3))

print("\n=== Win rate by evidence completeness bucket ===")
df["evidence_bucket"] = pd.cut(df["evidence_completeness"], bins=[0, 0.25, 0.5, 0.75, 1.0])
print(df.groupby("evidence_bucket")["won"].mean().round(3))

print("\n=== Win rate: festival vs non-festival ===")
print(df.groupby("festival_season")["won"].mean().round(3))

print("\n=== Amount stats ===")
print(df["amount"].describe().round(2))