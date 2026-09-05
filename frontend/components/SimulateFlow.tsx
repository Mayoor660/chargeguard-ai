"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { Dispute } from "@/lib/api";

const STEPS = [
  "Webhook verified",
  "Risk scored",
  "Evidence retrieved",
  "AI response generated",
  "Validation passed",
];

const STEP_DURATION_MS = 480; // 5 steps * 480ms ≈ 2.4s total

export default function SimulateFlow({ demos }: { demos: Dispute[] }) {
  const router = useRouter();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (activeId === null) return;

    if (stepIndex >= STEPS.length) {
      const t = setTimeout(
        () => router.push(`/disputes/${activeId}`),
        350
      );
      return () => clearTimeout(t);
    }

    const t = setTimeout(
      () => setStepIndex((i) => i + 1),
      STEP_DURATION_MS
    );

    return () => clearTimeout(t);
  }, [activeId, stepIndex, router]);

  function startAnalysis(id: string) {
    setStepIndex(0);
    setActiveId(id);
  }

  return (
    <>
      <div className="grid grid-cols-3 gap-4">
        {demos.map((d) => (
          <button
            key={d.razorpay_dispute_id}
            onClick={() => startAnalysis(d.razorpay_dispute_id)}
            className="text-left rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-5 hover:border-[var(--color-accent-blue)]/50 transition-colors cursor-pointer"
          >
            <div className="text-xs text-[var(--color-text-muted)] mb-1">
              {d.reason_code}
            </div>

            <div className="text-xl font-semibold">
              {d.win_probability !== null
                ? `${(d.win_probability * 100).toFixed(1)}%`
                : "—"}
            </div>
          </button>
        ))}
      </div>

      {activeId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-xl border border-[var(--color-border)] bg-[var(--color-bg-secondary)] p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-5">
              <ShieldCheck
                size={18}
                className="text-[var(--color-accent-blue)]"
              />

              <span className="text-sm font-medium">
                Analyzing {activeId}
              </span>
            </div>

            <div className="space-y-3">
              {STEPS.map((step, i) => {
                const done = i < stepIndex;
                const active = i === stepIndex;

                return (
                  <div
                    key={step}
                    className={`flex items-center gap-3 transition-opacity duration-300 ${
                      i > stepIndex
                        ? "opacity-30"
                        : "opacity-100"
                    }`}
                  >
                    {done ? (
                      <CheckCircle2
                        size={18}
                        className="text-[var(--color-success)] shrink-0"
                      />
                    ) : active ? (
                      <Loader2
                        size={18}
                        className="text-[var(--color-accent-blue)] shrink-0 animate-spin"
                      />
                    ) : (
                      <div className="w-[18px] h-[18px] rounded-full border border-[var(--color-border)] shrink-0" />
                    )}

                    <span
                      className={`text-sm ${
                        done
                          ? "text-[var(--color-text-secondary)]"
                          : "text-[var(--color-text-primary)]"
                      }`}
                    >
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </>
  );
}