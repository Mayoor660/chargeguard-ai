"use client";

import { useState, useMemo } from "react";
import { Search } from "lucide-react";
import { Dispute } from "@/lib/api";
import DisputeTable from "./DisputeTable";

export default function DisputesExplorer({ disputes }: { disputes: Dispute[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return disputes;
    return disputes.filter(
      (d) =>
        d.razorpay_dispute_id.toLowerCase().includes(q) ||
        d.reason_code.toLowerCase().includes(q) ||
        (d.payment_method ?? "").toLowerCase().includes(q)
    );
  }, [disputes, query]);

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search
          size={16}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
        />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by ID, reason, or method..."
          className="w-full pl-9 pr-3 py-2 rounded-md bg-[var(--color-bg-elevated)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent-blue)]/50"
        />
      </div>

      {filtered.length === 0 ? (
        <p className="text-sm text-[var(--color-text-secondary)] py-8 text-center">
          No disputes match &quot;{query}&quot;.
        </p>
      ) : (
        <DisputeTable disputes={filtered} />
      )}
    </div>
  );
}