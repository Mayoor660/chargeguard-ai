import { Validation } from "@/lib/api";
import { CheckCircle2, XCircle } from "lucide-react";

export default function ValidationStatus({ validation }: { validation: Validation }) {
  if (validation.passed) {
    return (
      <div className="rounded-lg bg-[var(--color-success-bg)] border border-[var(--color-success)]/30 px-4 py-3 flex items-start gap-2">
        <CheckCircle2 size={18} className="text-[var(--color-success)] mt-0.5 shrink-0" />
        <div className="text-sm">
          <div className="text-[var(--color-success)] font-medium">Validation Passed</div>
          <div className="text-[var(--color-text-secondary)] text-xs mt-0.5">
            Word count: {validation.word_count}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-[var(--color-danger-bg)] border border-[var(--color-danger)]/30 px-4 py-3">
      <div className="flex items-start gap-2">
        <XCircle size={18} className="text-[var(--color-danger)] mt-0.5 shrink-0" />
        <div className="text-sm">
          <div className="text-[var(--color-danger)] font-medium">Validation Failed</div>
          <div className="text-[var(--color-text-secondary)] text-xs mt-0.5">
            Word count: {validation.word_count}
          </div>
        </div>
      </div>
      {validation.issues.length > 0 && (
        <ul className="mt-2 ml-6 space-y-0.5">
          {validation.issues.map((issue, i) => (
            <li key={i} className="text-xs text-[var(--color-text-muted)]">
              - {issue}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}