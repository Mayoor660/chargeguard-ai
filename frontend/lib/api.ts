const API_BASE = "http://127.0.0.1:8000";

export interface EvidenceItem {
  title: string;
  text: string;
  evidence_type: string;
  similarity: number | null;
}

export interface Validation {
  word_count: number;
  issues: string[];
  passed: boolean;
}

export interface Dispute {
  razorpay_dispute_id: string;
  payment_id: string;
  reason_code: string;
  payment_method: string | null;
  amount: number;
  status: string;
  evidence_completeness: number;
  win_probability: number | null;
  evidence_letter: string | null;
  created_at: string | null;
}

export interface DisputeDetail extends Dispute {
  evidence_items: EvidenceItem[];
  validation: Validation;
}

export interface ShapContribution {
  feature: string;
  shap_value: number;
}

export interface ShapResponse {
  dispute_id: string;
  contributions: ShapContribution[];
}

export interface ReliabilityBucket {
  bucket: string;
  n: number;
  actual_win_rate: number;
  avg_predicted_prob: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export interface ModelMetrics {
  train_size: number;
  holdout_size: number;
  raw_model: { auc: number; brier_score: number };
  calibrated_model: { auc: number; brier_score: number };
  reliability_table: ReliabilityBucket[];
  top_feature_importances: FeatureImportance[];
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${path}`);
  }
  return res.json();
}

export function getDisputes(): Promise<Dispute[]> {
  return fetchJson<Dispute[]>("/api/disputes");
}

export function getDispute(id: string): Promise<DisputeDetail> {
  return fetchJson<DisputeDetail>(`/api/disputes/${id}`);
}

export function getDisputeShap(id: string): Promise<ShapResponse> {
  return fetchJson<ShapResponse>(`/api/disputes/${id}/shap`);
}

export function getModelMetrics(): Promise<ModelMetrics> {
  return fetchJson<ModelMetrics>("/api/model/metrics");
}