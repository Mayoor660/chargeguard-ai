import { getDisputes } from "@/lib/api";
import TopHeader from "@/components/TopHeader";
import SimulateFlow from "@/components/SimulateFlow";

export const dynamic = "force-dynamic";

export default async function SimulatePage() {
  const disputes = await getDisputes();

  const demoIds = [
    "disp_demo_low",
    "disp_simulated_002",
    "disp_demo_high",
  ];

  const demos = demoIds
    .map((id) =>
      disputes.find((d) => d.razorpay_dispute_id === id)
    )
    .filter(
      (d): d is NonNullable<typeof d> => Boolean(d)
    );

  return (
    <>
      <TopHeader
        title="Simulate Dispute"
        subtitle="Run a controlled dispute analysis scenario"
      />

      <main className="max-w-6xl mx-auto px-8 py-8 space-y-6">
        <section>
          <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-2">
            Select a scenario
          </h2>

          <p className="text-sm text-[var(--color-text-muted)] mb-5">
            Choose a pre-computed dispute to walk through the ChargeGuard
            analysis workflow.
          </p>

          <SimulateFlow demos={demos} />
        </section>
      </main>
    </>
  );
}