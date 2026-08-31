# ChargeGuard AI — AI-Powered Payment Dispute Risk & Evidence Response System

ChargeGuard helps merchants respond to payment disputes (chargebacks) faster and more effectively. When a dispute comes in, it estimates the probability of winning the dispute, retrieves the relevant evidence guidance for that dispute's reason code, drafts a representment letter using a local LLM, and explains the reasoning behind the score — all surfaced through a single dashboard.

Most merchants lose the majority of chargebacks not because they lack a case, but because they submit incomplete or poorly-targeted evidence under time pressure. ChargeGuard is built around that specific failure point: it doesn't just predict an outcome, it helps a merchant act on that prediction with the right evidence, in the right format, before the deadline.

> 🧪 **This is a prototype built for a portfolio/hackathon submission**, using synthetic data and a simulated Razorpay webhook. No real payment or customer data is involved anywhere in this project. See [Known Limitations](#known-limitations--future-work) below for what would change in a production deployment.

---

## What it does

Given a `payment.dispute.created` webhook event, ChargeGuard:

1. **Scores** the dispute's win probability using a calibrated XGBoost model trained on historical dispute outcomes
2. **Retrieves** relevant evidence-type guidance for that dispute's reason code from a vector knowledge base (Chroma + sentence-transformer embeddings)
3. **Drafts** a formal representment letter using a local LLM (Ollama / Llama 3.2), grounded only in the retrieved evidence — with deterministic post-processing to catch anything the LLM gets wrong
4. **Validates** the drafted letter (word count, evidence coverage) before it's shown to the user
5. **Explains** the score with SHAP feature attributions, so the win probability isn't a black box
6. **Recommends an action** (contest / manual review / gather more evidence) based on tuned probability thresholds, with an expected-value estimate of contesting

All of this is surfaced in a single Streamlit dashboard.

## Architecture

```
Razorpay Webhook (payment.dispute.created)
              │
              ▼
   Signature verification (HMAC)
              │
              ▼
   Win-probability model (XGBoost + Platt calibration)
              │
              ▼
   Evidence retrieval (Chroma vector DB, reason-code filtered)
              │
              ▼
   LLM letter composer (Ollama) + deterministic sanitizer
              │
              ▼
   Letter validator (word count, evidence coverage checks)
              │
              ▼
   SQLite (disputes table)
              │
              ▼
   Streamlit dashboard (risk assessment, evidence coverage,
   decision impact, drafted letter, validation status, SHAP)
```

**Why a raw + calibrated model pair?** The calibrated model (`CalibratedClassifierCV`, 5-fold sigmoid/Platt scaling) is what actually produces the win-probability shown to users — it's better calibrated, meaning a predicted 70% really does correspond to roughly a 70% actual win rate on the holdout set (see the reliability table in the dashboard's Model Performance panel). But it's an ensemble with no single clean decision path, so it can't be explained by SHAP directly. The raw, uncalibrated base XGBoost model (same features, same tree structure) is kept separately purely for SHAP explainability — "why" rather than "what probability."

## Dashboard features

- **Risk Assessment** — win probability, evidence completeness, and a recommended action (Contest / Manual Review / Gather More Evidence) based on tuned thresholds, explicitly labeled as prototype-tuned rather than industry-standard
- **Evidence Coverage** — which evidence types were retrieved from the knowledge base for this dispute's reason code, with approximate similarity scores from the vector retrieval step
- **Decision Impact** — expected value of contesting (win probability × disputed amount), as a simplified business-framing metric
- **Drafted Evidence Letter** — the LLM-generated representment letter, sanitized to remove any leftover placeholder text
- **AI Evidence Validation** — whether the letter passed automated checks (word count bounds, evidence presence), computed live from the same validation logic used at webhook time
- **SHAP Feature Contributions** — a per-dispute explanation of what drove the win-probability score
- **Model Performance** — holdout ROC-AUC, Brier score, reliability table, and top feature importances, read from the most recent training run
- **Quick Demo Scenarios** — three pre-loaded example disputes with different reason codes and payment methods

## Setup

### Prerequisites
- Python 3.11+ (conda environment recommended)
- [Ollama](https://ollama.com) installed and running locally, with the `llama3.2` model pulled (`ollama pull llama3.2`)

### Install

```bash
conda create -n chargeguard python=3.11
conda activate chargeguard
pip install -r requirements.txt
```

### Generate data and train the model

```bash
python scripts\generate_data.py
python scripts\feature_engineering.py
python scripts\train_model.py
python scripts\build_kb_index.py
```

This creates `data/features.csv`, trains and saves the win-probability model to `models/`, and builds the Chroma evidence knowledge base.

### Run the app

In one terminal, start the API server:
```bash
uvicorn chargeguard.api.main:app --reload
```

In a second terminal, start the dashboard:
```bash
streamlit run streamlit_app.py
```

In a third terminal, simulate an incoming dispute webhook:
```bash
python scripts\simulate_webhook.py
```

Open `http://localhost:8501` to view the dashboard.

You can also simulate different dispute scenarios:
```bash
python scripts\simulate_webhook.py --id disp_demo_low --reason credit_not_processed --amount 250000 --method credit_card
python scripts\simulate_webhook.py --id disp_demo_high --reason duplicate_processing --amount 899900 --method netbanking
```

## Model performance

Evaluated on a held-out test set of 10,000 disputes (never seen during training):

| Metric | Raw model | Calibrated model |
|---|---|---|
| ROC-AUC | 0.6809 | 0.6812 |
| Brier score | 0.2249 | 0.2248 |

An AUC of ~0.68 is an honest result, not a weak one: the synthetic training data has intentionally injected randomness, so a perfect predictor is neither achievable nor expected — a model that claimed 0.95+ AUC on this data would be evidence of a leakage bug, not a better model. The calibrated model's reliability table (visible in the dashboard) shows predicted probabilities track actual win rates closely across buckets, which matters more for this use case than raw discrimination power: a well-calibrated 60% should mean 60%, not just "more likely than a 40%."

The single strongest predictive feature by a wide margin is `evidence_completeness` (~34% importance), which is intentional — it reflects the real-world dynamic that evidence quality is the dominant factor in dispute outcomes, and is the reason the whole system is built around helping merchants improve that evidence rather than just scoring the dispute.

## Known limitations & future work

This was built under a compressed timeline as a portfolio/demo project. Known gaps, disclosed intentionally rather than discovered by a reviewer:

- **No background job queue.** The webhook handler runs scoring and LLM letter drafting synchronously inside the request. Razorpay expects a fast response from webhooks in production; a real deployment would offload this to a task queue (e.g. Celery + Redis) and return immediately.
- **No input validation on the webhook payload.** An empty or missing `reason_code` currently causes an unhandled exception (HTTP 500) rather than a clean validation error. Tested and confirmed this does **not** crash the server or write an incomplete record to the database, but it also doesn't return a useful error message. A production version would validate the payload with a Pydantic model before processing.
- **No graceful handling of LLM unavailability.** If Ollama isn't running, the letter-drafting step fails with an unhandled 500 rather than a clear error or fallback. A production version would add a retry/fallback path.
- **No production observability.** No metrics dashboards (Prometheus/Grafana), no experiment tracking (MLflow), no drift monitoring. Deliberately deferred as out of scope for a demo — mentioned here to be explicit about the trade-off, not because they were overlooked.
- **No test coverage target was pursued.** Testing in this project was done manually and interactively (integration flow, idempotency, restart survival, failure-mode testing) rather than as an automated suite with a coverage percentage.
- **Evidence retrieval similarity scores are on the lower side** (typically 0.2–0.4) for this demo's knowledge base, reflecting the use of a general-purpose sentence embedding model on short evidence-type descriptions rather than a domain-tuned retriever. Ranking is still sensible; the absolute similarity number is less meaningful than the ordering.
- **Single-currency, single-region assumptions.** Amounts are handled in INR/paise throughout; no multi-currency support.

## Tech stack

- **API:** FastAPI, SQLAlchemy, SQLite
- **ML:** XGBoost, scikit-learn (`CalibratedClassifierCV`), SHAP
- **RAG:** ChromaDB, sentence-transformers (`all-MiniLM-L6-v2`)
- **LLM:** Ollama (Llama 3.2), running locally
- **Dashboard:** Streamlit, Matplotlib
- **Data:** Synthetic dispute generator (PaySim-inspired), pandas

---

*Built as a submission exploring how AI can meaningfully help with payment dispute operations — not just as a fraud classifier, but as an end-to-end decision-support and evidence-response tool.*