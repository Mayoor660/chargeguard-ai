"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldCheck,
  LayoutGrid,
  ListChecks,
  Sparkles,
  Search,
  BarChart3,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Overview", href: "/", icon: LayoutGrid },
  { label: "Disputes", href: "/disputes", icon: ListChecks },
  { label: "Simulate Dispute", href: "/simulate", icon: Sparkles },
  { label: "Evidence Intelligence", href: "/evidence", icon: Search },
  { label: "Model Performance", href: "/model", icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-bg-secondary)] flex flex-col">
      <div className="px-5 py-5 flex items-center gap-2 border-b border-[var(--color-border)]">
        <ShieldCheck
          size={20}
          className="text-[var(--color-accent-blue)]"
        />
        <span className="font-semibold tracking-tight">
          ChargeGuard AI
        </span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.label}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-[var(--color-accent-blue)]/15 text-[var(--color-text-primary)] font-medium border border-[var(--color-accent-blue)]/30"
                  : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-5 py-4 border-t border-[var(--color-border)] text-[10px] text-[var(--color-text-muted)]">
        Synthetic data · Prototype
      </div>
    </aside>
  );
}