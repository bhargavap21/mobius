import { useMemo } from 'react'

function toneClass(tone) {
  if (tone === "pos") return "text-emerald-400";
  if (tone === "neg") return "text-red-400";
  return "text-emerald-300";
}

function buildPath(values, w, h, pad = 10) {
  if (!values.length) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const dx = (w - pad * 2) / (values.length - 1 || 1);
  const scaleY = (v) => {
    const t = max === min ? 0.5 : (v - min) / (max - min);
    return pad + (1 - t) * (h - pad * 2);
  };

  let d = `M ${pad} ${scaleY(values[0]).toFixed(2)}`;
  for (let i = 1; i < values.length; i++) {
    const x = pad + dx * i;
    const y = scaleY(values[i]);
    d += ` L ${x.toFixed(2)} ${y.toFixed(2)}`;
  }
  return d;
}

function buildArea(values, w, h, pad = 10) {
  if (!values.length) return "";
  const line = buildPath(values, w, h, pad);
  const lastX = w - pad;
  const firstX = pad;
  return `${line} L ${lastX} ${(h - pad).toFixed(2)} L ${firstX} ${(h - pad).toFixed(2)} Z`;
}

const CARDS = [
  {
    title: "Elon Tweet Trader",
    description: "Buy TSLA when Elon Musk tweets something positive about it.",
    // spiky step-ups + pullbacks (tweet-like jumps)
    chart: [22, 23, 23, 24, 26, 26, 27, 29, 28, 30, 30, 37, 36, 38, 39, 41, 40, 43, 45, 44, 48, 47, 55, 54, 58, 57, 61, 60, 66, 64],
    leftMetric: { label: "Backtest Score", value: "86/100", tone: "pos" },
    rightMetric: { label: "Risk Level", value: "Medium", tone: "neutral" },
    ctaLeft: "View More",
    ctaRight: "Deploy",
    subscribersLabel: "Remixes",
    subscribersCount: "291",
  },
  {
    title: "r/WallStreetBets Alpha",
    description: "Buy GME when r/WallStreetBets sentiment is bullish.",
    // high-volatility rollercoaster (WSB energy)
    chart: [30, 26, 34, 22, 40, 28, 46, 31, 52, 29, 58, 33, 49, 27, 61, 35, 55, 24, 63, 32, 57, 21, 66, 34, 60, 26, 70, 38, 62, 30],
    leftMetric: { label: "Signal Strength", value: "High", tone: "pos" },
    rightMetric: { label: "Volatility", value: "Very High", tone: "neg" },
    ctaLeft: "View More",
    ctaRight: "Deploy",
    subscribersLabel: "Remixes",
    subscribersCount: "342",
  },
  {
    title: "Mean Reversion",
    description: "Buy AAPL when RSI drops below 30 and sell when it's above 70.",
    // choppy, range-bound oscillation (mean reversion feel)
    chart: [50, 47, 52, 48, 53, 49, 54, 50, 55, 51, 54, 49, 53, 48, 52, 47, 51, 46, 50, 45, 49, 46, 50, 47, 51, 48, 52, 49, 51, 47],
    leftMetric: { label: "Win Rate", value: "57%", tone: "pos" },
    rightMetric: { label: "Max Drawdown", value: "-8.4%", tone: "neg" },
    ctaLeft: "View More",
    ctaRight: "Deploy",
    subscribersLabel: "Remixes",
    subscribersCount: "120",
  },
];

function StrategyCard({ data }) {
  const W = 520;
  const H = 260;
  const linePath = useMemo(() => buildPath(data.chart, W, H, 16), [data.chart]);
  const areaPath = useMemo(() => buildArea(data.chart, W, H, 16), [data.chart]);

  return (
    <div
      className="
        relative h-[420px] w-[340px] shrink-0
        rounded-[28px] border border-white/10
        bg-white/[0.06] backdrop-blur-xl
        shadow-[0_20px_60px_rgba(0,0,0,0.65)]
        overflow-hidden
      "
      style={{
        transform: "translateZ(0)",
      }}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-black/40 to-transparent" />

      <div className="relative z-10 px-6 pt-6">
        <div className="text-[20px] font-semibold tracking-tight text-white">{data.title}</div>
        <div className="mt-2 text-[12.5px] leading-[1.35] text-white/65">{data.description}</div>
      </div>

      <div className="absolute inset-x-0 bottom-0 top-[118px]">
        <div className="absolute inset-0">
          <div className="absolute -inset-10 bg-[radial-gradient(ellipse_at_center,rgba(16,185,129,0.25),transparent_60%)] blur-2xl" />
          <div className="absolute inset-x-0 bottom-0 h-[70%] bg-gradient-to-t from-emerald-500/20 via-emerald-500/10 to-transparent" />
        </div>

        <svg viewBox={`0 0 ${W} ${H}`} className="absolute inset-0 h-full w-full">
          <defs>
            <linearGradient id={`areaGrad-${data.title}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(16,185,129,0.35)" />
              <stop offset="75%" stopColor="rgba(16,185,129,0.06)" />
              <stop offset="100%" stopColor="rgba(16,185,129,0.00)" />
            </linearGradient>
            <filter id={`glow-${data.title}`}>
              <feGaussianBlur stdDeviation="3.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <path d={areaPath} fill={`url(#areaGrad-${data.title})`} />
          <path d={linePath} fill="none" stroke="rgba(16,185,129,0.95)" strokeWidth="3" filter={`url(#glow-${data.title})`} />
        </svg>

        <div className="absolute inset-x-4 bottom-[66px] rounded-2xl border border-white/10 bg-black/25 px-4 py-3 backdrop-blur-md">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="text-[11px] text-white/55">{data.leftMetric.label}</div>
              <div className={`mt-1 text-[18px] font-semibold ${toneClass(data.leftMetric.tone)}`}>
                {data.leftMetric.value}
              </div>
            </div>

            <div className="h-10 w-px bg-white/10" />

            <div className="min-w-0 text-right">
              <div className="text-[11px] text-white/55">{data.rightMetric.label}</div>
              <div className={`mt-1 text-[18px] font-semibold ${toneClass(data.rightMetric.tone)}`}>
                {data.rightMetric.value}
              </div>
            </div>
          </div>
        </div>

        <div className="absolute inset-x-5 bottom-5 flex items-center justify-between gap-3">
          <button
            className="
              flex-1 whitespace-nowrap
              rounded-full bg-white/10 px-4 py-2 text-[12px] font-medium text-white/80
              ring-1 ring-white/10 hover:bg-white/14 hover:text-white
              transition
            "
          >
            {data.ctaLeft}
          </button>

          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-2">
              <div className="text-[11px] text-white/45">{data.subscribersLabel}</div>
              <div className="flex -space-x-1">
                <span className="h-5 w-5 rounded-full bg-white/20 ring-1 ring-black/60" />
                <span className="h-5 w-5 rounded-full bg-white/15 ring-1 ring-black/60" />
                <span className="h-5 w-5 rounded-full bg-white/10 ring-1 ring-black/60" />
              </div>
              <div className="text-[11px] font-semibold text-white/70">{data.subscribersCount}</div>
            </div>

            <button
              className="
                rounded-full px-4 py-2 text-[12px] font-semibold text-white
                bg-gradient-to-r from-violet-600 to-fuchsia-500
                shadow-[0_10px_30px_rgba(168,85,247,0.35)]
                hover:brightness-110 transition
              "
            >
              {data.ctaRight}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function StrategyCarousel() {
  const items = useMemo(() => [...CARDS, ...CARDS, ...CARDS], []);

  return (
    <div className="relative w-full">
      <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-black to-transparent z-10" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-black to-transparent z-10" />

      <div className="relative [perspective:1200px]">
        <div
          className="
            marquee flex gap-8 py-8
            [transform:rotateX(8deg)]
          "
        >
          {items.map((c, idx) => (
            <div key={idx} className="will-change-transform">
              <StrategyCard data={c} />
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .marquee {
          width: max-content;
          animation: marqueeMove 26s linear infinite;
        }
        .marquee:hover { animation-play-state: paused; }
        @keyframes marqueeMove {
          from { transform: translateX(0) rotateX(8deg); }
          to   { transform: translateX(-33.333%) rotateX(8deg); }
        }
      `}</style>
    </div>
  );
}
