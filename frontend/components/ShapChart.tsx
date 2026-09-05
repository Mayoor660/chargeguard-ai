"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { ShapContribution } from "@/lib/api";

export default function ShapChart({ contributions }: { contributions: ShapContribution[] }) {
  const data = [...contributions].reverse(); // largest at top

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 30, top: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
          <XAxis
            type="number"
            stroke="var(--color-text-muted)"
            fontSize={11}
            tickFormatter={(v) => v.toFixed(2)}
          />
          <YAxis
            type="category"
            dataKey="feature"
            stroke="var(--color-text-muted)"
            fontSize={11}
            width={140}
          />
          <Tooltip
            contentStyle={{
              background: "var(--color-bg-elevated)",
              border: "1px solid var(--color-border)",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value) => Number(value).toFixed(4)}
          />
          <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.shap_value < 0 ? "var(--color-danger)" : "var(--color-success)"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}