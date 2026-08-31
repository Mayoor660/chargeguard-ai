"""
ChargeGuard Streamlit dashboard.

Run from the project root:
    streamlit run streamlit_app.py

Shows all disputes processed by the webhook pipeline, with filters by
reason code / payment method / win-probability range, and a detail view
per dispute including the drafted evidence letter and a SHAP explanation
of what drove that dispute's win-probability score.
"""

import json
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
import streamlit as st

from chargeguard.core.database import SessionLocal
from chargeguard.ml.scoring import build_feature_vector
from chargeguard.models.dispute import Dispute
from chargeguard.services.evidence_composer import retrieve_evidence, validate_letter

st.set_page_config(page_title="ChargeGuard Dashboard", layout="wide")


@st.cache_resource
def load_shap_explainer():
    raw_model = joblib.load("models/win_model_raw.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
    explainer = shap.Explainer(raw_model)
    return feature_columns, explainer


def load_disputes() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.query(Dispute).order_by(Dispute.created_at.desc()).all()
        data = [
            {
                "razorpay_dispute_id": r.razorpay_dispute_id,
                "payment_id": r.payment_id,
                "reason_code": r.reason_code,
                "payment_method": r.payment_method,
                "amount": r.amount,
                "status": r.status,
                "evidence_completeness": r.evidence_completeness,
                "win_probability": r.win_probability,
                "evidence_letter": r.evidence_letter,
                "created_at": r.created_at,
            }
            for r in rows
        ]
        return pd.DataFrame(data)
    finally:
        db.close()


def get_recommendation(win_prob: float) -> tuple[str, str, str]:
    """
    Returns (label, color, reason). Thresholds are our own tuned cutoffs
    for this demo -- not an industry standard -- chosen from the reliability
    table observed on the holdout set.
    """
    if win_prob is None:
        return "UNKNOWN", "gray", "No win probability available."
    if win_prob >= 0.75:
        return "CONTEST", "green", "Strong evidence signal — good candidate to formally contest."
    elif win_prob >= 0.45:
        return "MANUAL REVIEW", "orange", "Evidence is currently insufficient for automatic contest submission."
    else:
        return "GATHER MORE EVIDENCE", "red", "Low win probability — consider strengthening evidence before contesting, or accept the loss."


st.title("ChargeGuard — Dispute Dashboard")

st.warning(
    "🧪 **DEMO / SIMULATION MODE** — Transaction data and webhook events are simulated. "
    "No live payment or customer information is being processed.",
    icon="🧪",
)


with st.expander("📊 Model Performance (holdout evaluation)", expanded=False):
    try:
        with open("models/metrics.json") as f:
            metrics = json.load(f)

        st.caption(
            f"Evaluated on a held-out test set of {metrics['holdout_size']:,} disputes "
            f"(never seen during training)."
        )

        mcol1, mcol2 = st.columns(2)
        mcol1.metric(
            "ROC-AUC",
            f"{metrics['calibrated_model']['auc']:.4f}"
        )
        mcol2.metric(
            "Brier score",
            f"{metrics['calibrated_model']['brier_score']:.4f}"
        )

        st.caption(
            "An AUC of ~0.68 is honest, not weak: this model is trained on synthetic data "
            "with intentionally injected randomness, so it cannot and should not perfectly "
            "predict outcomes. The reliability table below shows the model is well-calibrated "
            "-- predicted probabilities track actual win rates closely across buckets."
        )

        st.markdown(
            "**Reliability table** "
            "(predicted probability vs. actual win rate)"
        )

        reliability_df = pd.DataFrame(
            metrics["reliability_table"]
        )

        st.dataframe(
            reliability_df.rename(
                columns={
                    "bucket": "Probability bucket",
                    "n": "Count",
                    "actual_win_rate": "Actual win rate",
                    "avg_predicted_prob": "Avg predicted probability",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            "**Top feature importances** "
            "(base XGBoost model)"
        )

        importance_df = pd.DataFrame(
            metrics["top_feature_importances"]
        )

        st.dataframe(
            importance_df.rename(
                columns={
                    "feature": "Feature",
                    "importance": "Importance",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    except FileNotFoundError:
        st.info(
            "Model metrics not found. Run "
            "`python scripts\\train_model.py` to generate "
            "models/metrics.json."
        )


df = load_disputes()

if df.empty:
    st.info(
        "No disputes yet. Trigger one with: python scripts\\simulate_webhook.py "
        "(with the FastAPI server running in another terminal)."
    )
    st.stop()


st.sidebar.header("Filters")

reason_options = sorted(
    df["reason_code"].dropna().unique().tolist()
)

selected_reasons = st.sidebar.multiselect(
    "Reason code",
    reason_options,
    default=reason_options
)

pay_options = sorted(
    df["payment_method"].dropna().unique().tolist()
)

selected_pay = st.sidebar.multiselect(
    "Payment method",
    pay_options,
    default=pay_options
)

prob_range = st.sidebar.slider(
    "Win probability range",
    0.0,
    1.0,
    (0.0, 1.0),
    step=0.05
)

filtered = df[
    df["reason_code"].isin(selected_reasons)
    & df["payment_method"].isin(selected_pay)
    & df["win_probability"]
    .fillna(0)
    .between(prob_range[0], prob_range[1])
]

st.subheader(f"Disputes ({len(filtered)})")

st.dataframe(
    filtered[
        [
            "razorpay_dispute_id",
            "reason_code",
            "payment_method",
            "amount",
            "win_probability",
            "status",
            "created_at",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.divider()

if filtered.empty:
    st.warning("No disputes match the current filters.")
    st.stop()

st.subheader("Dispute details")

st.markdown("**Quick demo scenarios**")

demo_col1, demo_col2, demo_col3 = st.columns(3)

demo_scenario = None

if demo_col1.button(
    "🔴 disp_demo_low (41.6%)",
    use_container_width=True
):
    demo_scenario = "disp_demo_low"

if demo_col2.button(
    "🟡 disp_simulated_002 (46.3%)",
    use_container_width=True
):
    demo_scenario = "disp_simulated_002"

if demo_col3.button(
    "🟢 disp_demo_high (50.2%)",
    use_container_width=True
):
    demo_scenario = "disp_demo_high"


dispute_ids = filtered["razorpay_dispute_id"].tolist()

default_index = (
    dispute_ids.index(demo_scenario)
    if demo_scenario in dispute_ids
    else 0
)

selected_id = st.selectbox(
    "Select a dispute to inspect",
    dispute_ids,
    index=default_index
)

row = filtered[
    filtered["razorpay_dispute_id"] == selected_id
].iloc[0]

col1, col2, col3 = st.columns(3)

win_prob = row["win_probability"]
evidence_completeness = row["evidence_completeness"] or 0.0

col1.metric(
    "Win probability",
    f"{win_prob:.1%}" if win_prob is not None else "N/A"
)

col2.metric(
    "Amount",
    f"₹{row['amount']:.2f}"
)

col3.metric(
    "Status",
    row["status"]
)

st.markdown(f"**Reason code:** {row['reason_code']}")
st.markdown(f"**Payment method:** {row['payment_method']}")

st.markdown("### Risk Assessment")

label, color, reason = get_recommendation(win_prob)

rcol1, rcol2, rcol3 = st.columns(3)

rcol1.metric(
    "Win probability",
    f"{win_prob:.1%}" if win_prob is not None else "N/A"
)

rcol2.metric(
    "Evidence completeness",
    f"{evidence_completeness:.0%}"
)

if color == "green":
    rcol3.success(f"**{label}**")
elif color == "orange":
    rcol3.warning(f"**{label}**")
else:
    rcol3.error(f"**{label}**")

st.caption(f"Reason: {reason}")

st.caption(
    "Thresholds (≥75% contest / 45–74% manual review / <45% gather more evidence) "
    "are tuned for this prototype based on the calibrated model's holdout reliability — "
    "not an industry-standard cutoff."
)

st.markdown("### Evidence Coverage")

coverage_items = (
    retrieve_evidence(row["reason_code"])
    if row["reason_code"]
    else []
)

if coverage_items:
    for item in coverage_items:
        sim_text = (
            f" — similarity: {item['similarity']:.2f}"
            if item.get("similarity") is not None
            else ""
        )

        st.markdown(
            f"✅ **{item['title']}** "
            f"({item['evidence_type']}){sim_text}"
        )

    st.caption(
        f"{len(coverage_items)} evidence type(s) retrieved from the "
        "knowledge base for this reason code. "
        "Similarity is an approximate score (1 − cosine distance) "
        "from the vector retrieval step."
    )
else:
    st.warning("⚠ No evidence types retrieved for this reason code.")


st.markdown("### Decision Impact")

expected_value = (win_prob or 0) * row["amount"]

ev_col1, ev_col2 = st.columns(2)

ev_col1.metric(
    "Potential dispute loss",
    f"₹{row['amount']:.2f}"
)

ev_col2.metric(
    "Expected value of contesting",
    f"₹{expected_value:.2f}"
)

st.caption(
    "Expected value = win probability × disputed amount. This is a simplified estimate "
    "that does not yet account for evidence-preparation cost or operational overhead."
)


st.markdown("### Drafted evidence letter")

st.text_area(
    "Letter",
    row["evidence_letter"] or "No letter drafted.",
    height=300,
    label_visibility="collapsed"
)


st.markdown("### AI Evidence Validation")

letter_text = row["evidence_letter"] or ""

evidence_items = (
    retrieve_evidence(row["reason_code"])
    if row["reason_code"]
    else []
)

validation = validate_letter(
    letter_text,
    evidence_items
)

if validation["passed"]:
    st.success(
        f"✅ Validation Passed  \n"
        f"Word count: {validation['word_count']}"
    )
else:
    st.error(
        f"❌ Validation Failed  \n"
        f"Word count: {validation['word_count']}"
    )

    for issue in validation["issues"]:
        st.caption(f"- {issue}")


st.markdown("### Why this score? (SHAP feature contributions)")

st.caption(
    "SHAP explanations use the underlying uncalibrated model for interpretability; "
    "the win probability shown above uses the calibrated model for accuracy."
)

feature_columns, explainer = load_shap_explainer()

feature_row = build_feature_vector(
    reason_code=row["reason_code"],
    payment_method=row["payment_method"],
    amount=row["amount"],
    created_at=row["created_at"],
    evidence_completeness=row["evidence_completeness"] or 0.5,
)

explanation = explainer(feature_row)

values = explanation.values[0]

contrib_df = (
    pd.DataFrame(
        {
            "feature": feature_columns,
            "shap_value": values,
        }
    )
    .sort_values(
        "shap_value",
        key=abs,
        ascending=False
    )
    .head(10)
)

fig, ax = plt.subplots(figsize=(7, 4))

colors = [
    "#d62728" if v < 0 else "#2ca02c"
    for v in contrib_df["shap_value"]
]

ax.barh(
    contrib_df["feature"],
    contrib_df["shap_value"],
    color=colors
)

ax.set_xlabel(
    "SHAP value (impact on model output)"
)

ax.invert_yaxis()

fig.tight_layout()

st.pyplot(fig)