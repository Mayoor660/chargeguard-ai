"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Database, SearchCheck, Loader2 } from "lucide-react";
import {
  Dispute,
  DisputeDetail,
  getDispute,
} from "@/lib/api";
import EvidenceCoverage from "./EvidenceCoverage";

export default function EvidenceExplorer({
  disputes,
}: {
  disputes: Dispute[];
}) {
  const [selectedId, setSelectedId] = useState(
    disputes[0]?.razorpay_dispute_id ?? ""
  );

  const [detail, setDetail] = useState<DisputeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }

    let cancelled = false;

    async function loadDetail() {
      setLoading(true);
      setError(null);

      try {
        const result = await getDispute(selectedId);

        if (!cancelled) {
          setDetail(result);
        }
      } catch (err) {
        if (!cancelled) {
          setDetail(null);
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load dispute evidence."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDetail();

    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const selected = disputes.find(
    (d) => d.razorpay_dispute_id === selectedId
  );

  if (!selected) {
    return (
      <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-6 text-sm text-[var(--color-text-secondary)]">
        No disputes available.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
        <div className="flex items-center gap-2 mb-4">
          <SearchCheck
            size={17}
            className="text-[var(--color-accent-purple)]"
          />
          <h2 className="text-sm font-medium">
            Evidence Retrieval
          </h2>
        </div>

        <label className="block text-xs text-[var(--color-text-muted)] mb-2">
          Select dispute
        </label>

        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          className="w-full max-w-md rounded-md bg-[var(--color-bg-elevated)] border border-[var(--color-border)] px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-blue)]/50"
        >
          {disputes.map((d) => (
            <option
              key={d.razorpay_dispute_id}
              value={d.razorpay_dispute_id}
            >
              {d.razorpay_dispute_id} — {d.reason_code}
            </option>
          ))}
        </select>
      </section>

      <section className="grid md:grid-cols-3 gap-4">
        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <div className="text-xs text-[var(--color-text-muted)] mb-1">
            Query
          </div>
          <div className="text-sm font-medium">
            {selected.reason_code.replaceAll("_", " ")}
          </div>
        </div>

        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <div className="text-xs text-[var(--color-text-muted)] mb-1">
            Retrieval source
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <Database
              size={15}
              className="text-[var(--color-accent-blue)]"
            />
            Chroma knowledge base
          </div>
        </div>

        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
          <div className="text-xs text-[var(--color-text-muted)] mb-1">
            Retrieved items
          </div>

          {loading ? (
            <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <Loader2 size={15} className="animate-spin" />
              Loading evidence...
            </div>
          ) : (
            <div className="text-2xl font-semibold">
              {detail?.evidence_items.length ?? 0}
            </div>
          )}
        </div>
      </section>

      {error && (
        <div className="rounded-lg border border-[var(--color-danger)]/30 bg-[var(--color-danger-bg)] p-4 text-sm text-[var(--color-danger)]">
          {error}
        </div>
      )}

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
        <h2 className="text-sm font-medium text-[var(--color-text-secondary)] mb-4">
          Retrieved Evidence
        </h2>

        {loading ? (
          <div className="flex items-center gap-2 py-6 text-sm text-[var(--color-text-secondary)]">
            <Loader2 size={16} className="animate-spin" />
            Retrieving evidence...
          </div>
        ) : (
          <EvidenceCoverage items={detail?.evidence_items ?? []} />
        )}
      </section>

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h2 className="text-sm font-medium mb-1">
              Continue investigation
            </h2>

            <p className="text-xs text-[var(--color-text-muted)]">
              Open the complete dispute intelligence view.
            </p>
          </div>

          <Link
            href={`/disputes/${selected.razorpay_dispute_id}`}
            className="inline-flex items-center gap-1.5 rounded-md border border-[var(--color-border)] px-3 py-2 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-accent-blue)] hover:border-[var(--color-accent-blue)]/40 transition-colors"
          >
            Open dispute
            <ArrowRight size={13} />
          </Link>
        </div>
      </section>
    </div>
  );
}