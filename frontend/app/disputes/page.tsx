import { getDisputes } from "@/lib/api";
import TopHeader from "@/components/TopHeader";
import DisputesExplorer from "@/components/DisputesExplorer";

export const dynamic = "force-dynamic";

export default async function DisputesPage() {
  const disputes = await getDisputes();
  const visibleDisputes = disputes.filter((d) => !d.razorpay_dispute_id.startsWith("disp_test_"));

  return (
    <>
      <TopHeader title="Disputes" subtitle={`${visibleDisputes.length} disputes in the demo dataset`} />
      <main className="max-w-6xl mx-auto px-8 py-8">
        <DisputesExplorer disputes={visibleDisputes} />
      </main>
    </>
  );
}