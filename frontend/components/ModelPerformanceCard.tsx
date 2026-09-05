"use client";

import { useState } from "react";
import { ModelMetrics } from "@/lib/api";
import { ChevronDown, ChevronRight, BarChart3 } from "lucide-react";
import ModelPerformanceContent from "./ModelPerformanceContent";

export default function ModelPerformanceCard({ metrics }: { metrics: ModelMetrics }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-4 py-3 text-left">
        <span className="flex items-center gap-2 font-medium">
          <BarChart3 size={16} className="text-[var(--color-accent-purple)]" />
          Model Performance (holdout evaluation)
        </span>
        {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
      </button>

      {open && (
        <div className="px-4 pb-4">
          <ModelPerformanceContent metrics={metrics} />
        </div>
      )}
    </div>
  );
}