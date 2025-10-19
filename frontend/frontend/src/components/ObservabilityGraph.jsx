"use client";

import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from "recharts";
import { useMemo } from "react";

// mock demo data (replace via props later if needed)
function useDemoData() {
  return useMemo(() => {
    const now = new Date();
    const sixMonthsAgo = new Date(now);
    sixMonthsAgo.setMonth(now.getMonth() - 6);
    
    return Array.from({ length: 30 }).map((_, i) => {
      const date = new Date(sixMonthsAgo);
      date.setDate(sixMonthsAgo.getDate() + (i * 6)); // ~6 days apart
      
      return {
        name: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        mobius: 10000 + Math.round(6000 * Math.sin(i / 3) + Math.random() * 2000),
        manual: 5000 + Math.round(3000 * Math.cos(i / 4) + Math.random() * 1500),
      };
    });
  }, []);
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
        <h3 className="text-3xl md:text-4xl font-light tracking-tight text-white">{title}</h3>
        <p className="mt-2 text-base text-gray-400">See how Mobius AI-powered trading bots outperform manual trading strategies</p>
      </header>

      <div className="h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="name" stroke="rgba(255,255,255,0.35)" tickMargin={8} />
            <YAxis
              stroke="rgba(255,255,255,0.35)"
              width={44}
              domain={[0, 20000]}
              ticks={[0, 5000, 10000, 15000, 20000]}
              tickFormatter={(v) => `${v / 1000}k`}
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
            {/* Series colors: purple for Mobius, white for Manual Trading */}
            <Line
              type="monotone"
              dataKey="mobius"
              name="Mobius"
              stroke="#7c3aed"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="manual"
              name="Manual Trading"
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

