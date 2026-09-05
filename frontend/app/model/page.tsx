import { getModelMetrics } from "@/lib/api";
import TopHeader from "@/components/TopHeader";
import ModelPerformanceContent from "@/components/ModelPerformanceContent";

export const dynamic = "force-dynamic";

export default async function ModelPage() {
  const metrics = await getModelMetrics();

  return (
    <>
      <TopHeader
        title="Model Performance"
        subtitle="Holdout evaluation and calibration"
      />

      <main className="max-w-6xl mx-auto px-8 py-8">
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-6">
          <ModelPerformanceContent metrics={metrics} />
        </section>
      </main>
    </>
  );
}