import { RiskLevel } from "@/lib/risk";

const styles: Record<RiskLevel, string> = {
  contest: "bg-[var(--color-success-bg)] text-[var(--color-success)] border-[var(--color-success)]/30",
  review: "bg-[var(--color-warning-bg)] text-[var(--color-warning)] border-[var(--color-warning)]/30",
  gather: "bg-[var(--color-danger-bg)] text-[var(--color-danger)] border-[var(--color-danger)]/30",
};

export default function RiskBadge({ label, level }: { label: string; level: RiskLevel }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold border ${styles[level]}`}>
      {label}
    </span>
  );
}