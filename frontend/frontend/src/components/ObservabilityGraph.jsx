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
      className="mx-auto mt-0 w-full max-w-6xl p-6 md:p-8"
    >
      <header className="mb-8 text-center">
        <h3 className="text-4xl md:text-5xl font-light tracking-tight text-white">{title}</h3>
        <p className="mt-4 text-base text-white/60">See how Mobius AI-powered trading bots outperform manual trading strategies</p>
      </header>

      {/* Glassmorphism card with neon aurora glow */}
      <div className="relative rounded-3xl border border-white/10 bg-white/[0.02] p-8 backdrop-blur-xl">
        {/* Aurora glow effects */}
        <div className="pointer-events-none absolute -top-40 left-1/4 h-80 w-80 rounded-full bg-violet-500/30 blur-[120px]" />
        <div className="pointer-events-none absolute -bottom-40 right-1/4 h-80 w-80 rounded-full bg-emerald-500/20 blur-[120px]" />

        {/* Inner vignette */}
        <div className="pointer-events-none absolute inset-0 rounded-3xl bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.03),transparent_70%)] opacity-40" />

        <div className="relative h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} strokeDasharray="3 3" />
              <XAxis
                dataKey="name"
                stroke="rgba(255,255,255,0.4)"
                tickMargin={12}
                style={{ fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 300 }}
              />
              <YAxis
                stroke="rgba(255,255,255,0.4)"
                width={50}
                domain={[0, 20000]}
                ticks={[0, 5000, 10000, 15000, 20000]}
                tickFormatter={(v) => `${v / 1000}k`}
                tickMargin={12}
                style={{ fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 300 }}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(10, 10, 10, 0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 16,
                  color: "white",
                  backdropFilter: "blur(12px)",
                  boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 300,
                }}
                labelStyle={{ color: "rgba(255,255,255,0.6)", marginBottom: '8px' }}
              />
              <Legend
                wrapperStyle={{
                  color: "rgba(255,255,255,0.6)",
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                  fontWeight: 300,
                  paddingTop: '16px'
                }}
                iconType="circle"
              />
              {/* Neon purple for Mobius */}
              <Line
                type="monotone"
                dataKey="mobius"
                name="Mobius"
                stroke="#8b5cf6"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: "#8b5cf6", stroke: "#c084fc", strokeWidth: 2 }}
                filter="drop-shadow(0 0 8px rgba(139, 92, 246, 0.6))"
              />
              {/* Subtle white for Manual Trading */}
              <Line
                type="monotone"
                dataKey="manual"
                name="Manual Trading"
                stroke="rgba(255,255,255,0.5)"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5, fill: "#ffffff", stroke: "#e5e7eb", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

