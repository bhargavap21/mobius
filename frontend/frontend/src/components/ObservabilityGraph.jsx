"use client";

import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from "recharts";
import { useMemo } from "react";

// mock demo data (replace via props later if needed)
function useDemoData() {
  return useMemo(
    () =>
      Array.from({ length: 30 }).map((_, i) => ({
        name: `T${i + 1}`,
        homepage: 200 + Math.round(60 * Math.sin(i / 3) + Math.random() * 40),
        checkout: 110 + Math.round(40 * Math.cos(i / 4) + Math.random() * 30),
      })),
    []
  );
}

export default function ObservabilityGraph({
  title = "Route-aware observability.",
  subtitle = "Monitor and analyze the performance and traffic of your projects.",
}) {
  const data = useDemoData();

  return (
    <section
      aria-label="Observability graph"
      className="mx-auto mt-0 w-full max-w-6xl rounded-2xl bg-transparent p-6 md:p-8"
    >
      <header className="mb-6">
        <p className="text-sm text-fg-muted">📈 Observability</p>
        <h3 className="mt-2 text-2xl font-light tracking-tight text-fg">{title}</h3>
        <p className="mt-1 text-sm text-fg-muted">{subtitle}</p>
      </header>

      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="name" stroke="rgba(255,255,255,0.35)" tickMargin={8} />
            <YAxis
              stroke="rgba(255,255,255,0.35)"
              width={44}
              tickFormatter={(v) => `${v}k`}
              tickMargin={8}
            />
            <Tooltip
              contentStyle={{
                background: "#111318",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
                color: "white",
              }}
              labelStyle={{ color: "rgba(255,255,255,0.7)" }}
            />
            <Legend
              wrapperStyle={{ color: "rgba(255,255,255,0.7)" }}
              iconType="circle"
            />
            {/* Series colors: purple + amber to mirror the reference */}
            <Line
              type="monotone"
              dataKey="homepage"
              name="Homepage"
              stroke="#7c3aed"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="checkout"
              name="Checkout"
              stroke="#ffffff"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

