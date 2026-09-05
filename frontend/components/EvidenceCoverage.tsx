import { EvidenceItem } from "@/lib/api";
import { CheckCircle2 } from "lucide-react";

export default function EvidenceCoverage({ items }: { items: EvidenceItem[] }) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-[var(--color-text-secondary)]">
        No evidence types retrieved for this reason code.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.evidence_type} className="flex items-start gap-3">
          <CheckCircle2 size={18} className="text-[var(--color-success)] mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="flex items-baseline gap-2 flex-wrap">
              <span className="font-medium text-sm">{item.title}</span>
              <span className="text-xs text-[var(--color-text-muted)]">({item.evidence_type})</span>
              {item.similarity !== null && (
                <span className="text-xs text-[var(--color-accent-blue)]">
                  similarity: {item.similarity.toFixed(2)}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
      <p className="text-xs text-[var(--color-text-muted)] pt-1">
        {items.length} evidence type(s) retrieved from the knowledge base for this reason code. Similarity is an
        approximate score (1 − cosine distance) from the vector retrieval step.
      </p>
    </div>
  );
}