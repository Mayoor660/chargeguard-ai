import { getDisputes } from "@/lib/api";
import TopHeader from "@/components/TopHeader";
import EvidenceExplorer from "@/components/EvidenceExplorer";

export const dynamic = "force-dynamic";

export default async function EvidencePage() {
  const disputes = await getDisputes();

  const visibleDisputes = disputes.filter(
    (d) => !d.razorpay_dispute_id.startsWith("disp_test_")
  );

  return (
    <>
      <TopHeader
        title="Evidence Intelligence"
        subtitle="Retrieve and inspect dispute evidence"
      />

      <main className="max-w-6xl mx-auto px-8 py-8">
        <EvidenceExplorer disputes={visibleDisputes} />
      </main>
    </>
  );
}