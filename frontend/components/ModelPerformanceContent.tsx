import { ModelMetrics } from "@/lib/api";

export default function ModelPerformanceContent({ metrics }: { metrics: ModelMetrics }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--color-text-secondary)]">
        Evaluated on a held-out test set of {metrics.holdout_size.toLocaleString()} disputes (never seen during
        training).
      </p>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-md bg-[var(--color-bg-elevated)] p-4">
          <div className="text-xs text-[var(--color-text-muted)] mb-1">ROC-AUC</div>
          <div className="text-2xl font-semibold">{metrics.calibrated_model.auc.toFixed(4)}</div>
        </div>
        <div className="rounded-md bg-[var(--color-bg-elevated)] p-4">
          <div className="text-xs text-[var(--color-text-muted)] mb-1">Brier Score</div>
          <div className="text-2xl font-semibold">{metrics.calibrated_model.brier_score.toFixed(4)}</div>
        </div>
      </div>

      <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
        An AUC of ~0.68 is honest, not weak: this model is trained on synthetic data with intentionally injected
        randomness, so it cannot and should not perfectly predict outcomes. The reliability table below shows the
        model is well-calibrated — predicted probabilities track actual win rates closely across buckets.
      </p>

      <div>
        <h4 className="text-sm font-medium mb-2">Reliability table</h4>
        <div className="overflow-x-auto rounded-md border border-[var(--color-border)]">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)]">
                <th className="px-3 py-2 text-left font-medium">Bucket</th>
                <th className="px-3 py-2 text-left font-medium">Count</th>
                <th className="px-3 py-2 text-left font-medium">Actual win rate</th>
                <th className="px-3 py-2 text-left font-medium">Avg predicted</th>
              </tr>
            </thead>
            <tbody>
              {metrics.reliability_table.map((r) => (
                <tr key={r.bucket} className="border-t border-[var(--color-border)]">
                  <td className="px-3 py-2">{r.bucket}</td>
                  <td className="px-3 py-2">{r.n}</td>
                  <td className="px-3 py-2">{r.actual_win_rate.toFixed(3)}</td>
                  <td className="px-3 py-2">{r.avg_predicted_prob.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium mb-2">Top feature importances</h4>
        <div className="space-y-1.5">
          {metrics.top_feature_importances.slice(0, 6).map((f) => (
            <div key={f.feature} className="flex items-center gap-2 text-xs">
              <span className="w-40 truncate text-[var(--color-text-secondary)]">{f.feature}</span>
              <div className="flex-1 h-1.5 bg-[var(--color-bg-elevated)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[var(--color-accent-purple)]"
                  style={{ width: `${(f.importance / metrics.top_feature_importances[0].importance) * 100}%` }}
                />
              </div>
              <span className="w-14 text-right text-[var(--color-text-muted)]">{f.importance.toFixed(4)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}