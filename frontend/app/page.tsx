import Link from "next/link";
import { getDisputes, getModelMetrics } from "@/lib/api";
import { getRecommendation } from "@/lib/risk";
import DisputeTable from "@/components/DisputeTable";
import ModelPerformanceCard from "@/components/ModelPerformanceCard";
import SimulateFlow from "@/components/SimulateFlow";
import TopHeader from "@/components/TopHeader";
import {
  ShieldAlert,
  ShieldCheck,
  ShieldQuestion,
  FileText,
  TrendingUp,
  IndianRupee,
} from "lucide-react";

export const dynamic = "force-dynamic";

export default async function Overview() {
  const [disputes, metrics] = await Promise.all([getDisputes(), getModelMetrics()]);

  // Internal test/debug disputes are kept in the database (evidence of edge-case
  // testing) but hidden from this presentation view. See README "Known Limitations."
  const visibleDisputes = disputes.filter((d) => !d.razorpay_dispute_id.startsWith("disp_test_"));

  const avgWinProb =
    visibleDisputes.reduce((sum, d) => sum + (d.win_probability ?? 0), 0) / (visibleDisputes.length || 1);

  const demoIds = ["disp_demo_low", "disp_simulated_002", "disp_demo_high"];
  const demoScenarios = demoIds
    .map((id) => visibleDisputes.find((d) => d.razorpay_dispute_id === id))
    .filter((d): d is NonNullable<typeof d> => Boolean(d));

  const recCounts = { contest: 0, review: 0, gather: 0 };
  for (const d of visibleDisputes) {
    recCounts[getRecommendation(d.win_probability).level]++;
  }

  return (
    <>
      <TopHeader
        title="ChargeGuard"
        subtitle="AI-Powered Payment Dispute Risk & Evidence Response System"
      />

      <main className="max-w-6xl mx-auto px-8 py-8 space-y-8">
        

        <div className="grid grid-cols-4 gap-4">
          <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="text-xs text-[var(--color-text-muted)]">Total Disputes</div>
              <div className="w-8 h-8 rounded-md bg-[var(--color-accent-blue)]/15 flex items-center justify-center">
                <FileText size={15} className="text-[var(--color-accent-blue)]" />
              </div>
            </div>
            <div className="text-2xl font-semibold">{visibleDisputes.length}</div>
            <div className="text-xs text-[var(--color-text-muted)] mt-1">Active disputes</div>
          </div>

          <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="text-xs text-[var(--color-text-muted)]">Avg. Win Probability</div>
              <div className="w-8 h-8 rounded-md bg-[var(--color-accent-purple)]/15 flex items-center justify-center">
                <TrendingUp size={15} className="text-[var(--color-accent-purple)]" />
              </div>
            </div>
            <div className="text-2xl font-semibold">{(avgWinProb * 100).toFixed(1)}%</div>
            <div className="text-xs text-[var(--color-text-muted)] mt-1">Across all disputes</div>
          </div>

          <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="text-xs text-[var(--color-text-muted)]">Total Amount at Risk</div>
              <div className="w-8 h-8 rounded-md bg-[var(--color-accent-blue)]/15 flex items-center justify-center">
                <IndianRupee size={15} className="text-[var(--color-accent-blue)]" />
              </div>
            </div>
            <div className="text-2xl font-semibold">
              ₹{visibleDisputes.reduce((s, d) => s + d.amount, 0).toFixed(2)}
            </div>
            <div className="text-xs text-[var(--color-text-muted)] mt-1">Across all disputes</div>
          </div>

          <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="text-xs text-[var(--color-text-muted)]">High Risk Disputes</div>
              <div className="w-8 h-8 rounded-md bg-[var(--color-danger)]/15 flex items-center justify-center">
                <ShieldAlert size={15} className="text-[var(--color-danger)]" />
              </div>
            </div>
            <div className="text-2xl font-semibold">{recCounts.gather}</div>
            <div className="text-xs text-[var(--color-text-muted)] mt-1">Win probability &lt; 45%</div>
          </div>
        </div>

        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">Recommendation Summary</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-md bg-[var(--color-success-bg)] flex items-center justify-center shrink-0">
                <ShieldCheck size={16} className="text-[var(--color-success)]" />
              </div>
              <div>
                <div className="text-lg font-semibold">{recCounts.contest}</div>
                <div className="text-xs text-[var(--color-text-muted)]">Contest</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-md bg-[var(--color-warning-bg)] flex items-center justify-center shrink-0">
                <ShieldQuestion size={16} className="text-[var(--color-warning)]" />
              </div>
              <div>
                <div className="text-lg font-semibold">{recCounts.review}</div>
                <div className="text-xs text-[var(--color-text-muted)]">Manual Review</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-md bg-[var(--color-danger-bg)] flex items-center justify-center shrink-0">
                <ShieldAlert size={16} className="text-[var(--color-danger)]" />
              </div>
              <div>
                <div className="text-lg font-semibold">{recCounts.gather}</div>
                <div className="text-xs text-[var(--color-text-muted)]">Gather More Evidence</div>
              </div>
            </div>
          </div>
        </div>

        <ModelPerformanceCard metrics={metrics} />

        <section>
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-3">Quick  scenarios</h2>
          <SimulateFlow demos={demoScenarios} />
        </section>

        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-[var(--color-text-secondary)]">Recent disputes</h2>
            <Link href="/disputes" className="text-xs text-[var(--color-accent-blue)] hover:underline">
              View All Disputes →
            </Link>
          </div>
          <DisputeTable disputes={visibleDisputes} />
        </section>
      </main>
    </>
  );
}