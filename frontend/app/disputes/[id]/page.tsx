import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getDispute, getDisputeShap } from "@/lib/api";
import { getRecommendation } from "@/lib/risk";
import RiskBadge from "@/components/RiskBadge";
import EvidenceCoverage from "@/components/EvidenceCoverage";
import DecisionImpact from "@/components/DecisionImpact";
import ValidationStatus from "@/components/ValidationStatus";
import ShapChart from "@/components/ShapChart";
import TopHeader from "@/components/TopHeader";

export const dynamic = "force-dynamic";

export default async function DisputeDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [dispute, shap] = await Promise.all([getDispute(id), getDisputeShap(id)]);

  const rec = getRecommendation(dispute.win_probability);

  return (
    <>
      <TopHeader title={dispute.razorpay_dispute_id} subtitle="Dispute Intelligence" />

      <main className="max-w-5xl mx-auto px-8 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            <ArrowLeft size={14} />
            Back to Overview
          </Link>
          <RiskBadge label={rec.label} level={rec.level} />
        </div>

        <p className="text-sm text-[var(--color-text-secondary)]">
          {dispute.reason_code} · {dispute.payment_method} · {dispute.status}
        </p>

        {/* Risk Assessment */}
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">Risk Assessment</h2>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <div className="text-xs text-[var(--color-text-muted)] mb-1">Win probability</div>
              <div className="text-2xl font-semibold">
                {dispute.win_probability !== null ? `${(dispute.win_probability * 100).toFixed(1)}%` : "—"}
              </div>
            </div>
            <div>
              <div className="text-xs text-[var(--color-text-muted)] mb-1">Evidence completeness</div>
              <div className="text-2xl font-semibold">{(dispute.evidence_completeness * 100).toFixed(0)}%</div>
            </div>
            <div>
              <div className="text-xs text-[var(--color-text-muted)] mb-1">Amount</div>
              <div className="text-2xl font-semibold">₹{dispute.amount.toFixed(2)}</div>
            </div>
          </div>
          <p className="text-sm text-[var(--color-text-secondary)]">{rec.reason}</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-2">
            Thresholds (≥75% contest / 45–74% manual review / &lt;45% gather more evidence) are tuned for this
            prototype based on the calibrated model&apos;s holdout reliability — not an industry-standard cutoff.
          </p>
        </section>

        {/* Evidence Coverage */}
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">Evidence Coverage</h2>
          <EvidenceCoverage items={dispute.evidence_items} />
        </section>

        {/* Decision Impact */}
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">Decision Impact</h2>
          <DecisionImpact winProb={dispute.win_probability} amount={dispute.amount} />
        </section>

        {/* Drafted Letter */}
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">Drafted Evidence Letter</h2>
          <div className="rounded-md bg-[var(--color-bg-elevated)] p-4 text-sm leading-relaxed whitespace-pre-line text-[var(--color-text-primary)] max-h-96 overflow-y-auto">
            {dispute.evidence_letter || "No letter drafted."}
          </div>
        </section>

        {/* AI Validation */}
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">AI Evidence Validation</h2>
          <ValidationStatus validation={dispute.validation} />
        </section>

        {/* SHAP */}
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-1">
            Why this score? (SHAP feature contributions)
          </h2>
          <p className="text-xs text-[var(--color-text-muted)] mb-4">
            SHAP explanations use the underlying uncalibrated model for interpretability; the win probability shown
            above uses the calibrated model for accuracy.
          </p>
          <ShapChart contributions={shap.contributions} />
        </section>
      </main>
    </>
  );
}