"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Dispute } from "@/lib/api";
import { getRecommendation } from "@/lib/risk";
import RiskBadge from "./RiskBadge";

export default function DisputeTable({ disputes }: { disputes: Dispute[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-[var(--color-border)]">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] text-left">
            <th className="px-4 py-3 font-medium">Dispute ID</th>
            <th className="px-4 py-3 font-medium">Reason</th>
            <th className="px-4 py-3 font-medium">Method</th>
            <th className="px-4 py-3 font-medium">Amount</th>
            <th className="px-4 py-3 font-medium">Win Prob.</th>
            <th className="px-4 py-3 font-medium">Recommendation</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Action</th>
          </tr>
        </thead>
        <tbody>
          {disputes.map((d) => {
            const rec = getRecommendation(d.win_probability);
            const isOpen = d.status.toLowerCase() === "open";
            return (
              <tr
                key={d.razorpay_dispute_id}
                className="border-t border-[var(--color-border)] hover:bg-[var(--color-bg-elevated)] transition-colors"
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/disputes/${d.razorpay_dispute_id}`}
                    className="text-[var(--color-accent-blue)] hover:underline font-medium"
                  >
                    {d.razorpay_dispute_id}
                  </Link>
                </td>
                <td className="px-4 py-3 text-[var(--color-text-secondary)]">{d.reason_code}</td>
                <td className="px-4 py-3 text-[var(--color-text-secondary)]">{d.payment_method}</td>
                <td className="px-4 py-3">₹{d.amount.toFixed(2)}</td>
                <td className="px-4 py-3 font-medium">
                  {d.win_probability !== null ? `${(d.win_probability * 100).toFixed(1)}%` : "—"}
                </td>
                <td className="px-4 py-3">
                  <RiskBadge label={rec.label} level={rec.level} />
                </td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1.5 text-[var(--color-text-secondary)] capitalize">
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        isOpen ? "bg-[var(--color-success)]" : "bg-[var(--color-text-muted)]"
                      }`}
                    />
                    {d.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/disputes/${d.razorpay_dispute_id}`}
                    className="inline-flex items-center gap-1 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-accent-blue)] border border-[var(--color-border)] rounded-md px-2 py-1 transition-colors"
                  >
                    Open <ArrowRight size={12} />
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}