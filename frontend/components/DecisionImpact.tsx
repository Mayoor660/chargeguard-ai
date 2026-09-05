export default function DecisionImpact({ winProb, amount }: { winProb: number | null; amount: number }) {
  const expectedValue = (winProb ?? 0) * amount;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-xs text-[var(--color-text-muted)] mb-1">Potential dispute loss</div>
          <div className="text-xl font-semibold">₹{amount.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-xs text-[var(--color-text-muted)] mb-1">Expected value of contesting</div>
          <div className="text-xl font-semibold">₹{expectedValue.toFixed(2)}</div>
        </div>
      </div>
      <p className="text-xs text-[var(--color-text-muted)]">
        Expected value = win probability × disputed amount. This is a simplified estimate that does not yet account
        for evidence-preparation cost or operational overhead.
      </p>
    </div>
  );
}