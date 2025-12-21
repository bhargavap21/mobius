import React from "react";

export function ManualWorkflowMockChaos() {
  return (
    <div className="relative h-full w-full overflow-hidden border border-white/10 bg-white/[0.05] backdrop-blur-xl shadow-[0_25px_80px_rgba(0,0,0,0.75)] rounded-[40px]">
      {/* animated noise + scanlines */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.08] mix-blend-overlay noise" />
      <div className="pointer-events-none absolute inset-0 opacity-[0.08] scanlines" />

      {/* main grid - now full height with minimal padding */}
      <div className="relative z-10 grid h-full grid-cols-12 gap-3 p-4">
        {/* left column: "browser + chart + logs" */}
        <div className="relative col-span-7 overflow-hidden rounded-3xl border border-white/10 bg-black/35 backdrop-blur">
          {/* faux chrome */}
          <div className="flex items-center gap-3 border-b border-white/10 bg-white/[0.04] px-4 py-2">
            <div className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-red-400/70" />
              <span className="h-2 w-2 rounded-full bg-yellow-300/70" />
              <span className="h-2 w-2 rounded-full bg-emerald-300/70" />
            </div>

            <div className="flex min-w-0 flex-1 items-center gap-2 overflow-hidden">
              <Tab active label="Backtest Notebook" />
              <Tab label="TradingView" />
              <Tab label="WSB sentiment" />
              <Tab label="Alpaca Docs" />
              <Tab label="Google Sheet" />
              <Tab label="X / Tweets" />
            </div>

            <div className="text-[10px] text-white/35 whitespace-nowrap">⌘K</div>
          </div>

          <div className="grid grid-cols-12 gap-3 p-3">
            {/* chart panel */}
            <div className="relative col-span-7 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div className="flex items-center justify-between">
                <div className="text-[13px] font-semibold text-white/70">AAPL • 1D • RSI(14)</div>
                <div className="flex items-center gap-2 text-[11px] text-white/40">
                  <span className="rounded-full border border-white/10 bg-black/30 px-2 py-1">paper</span>
                  <span className="rounded-full border border-white/10 bg-black/30 px-2 py-1">v2.7</span>
                </div>
              </div>

              <div className="mt-2">
                <FakeChartSuperBusy />
              </div>

              <div className="mt-2 flex flex-wrap gap-2">
                <Pill label="RSI" value="29.7" tone="good" />
                <Pill label="Vol" value="+18%" tone="warn" />
                <Pill label="Regime" value="MeanRev" tone="neutral" />
                <Pill label="Slippage" value="0.03%" tone="warn" />
                <Pill label="Latency" value="420ms" tone="bad" />
              </div>

              {/* cursor highlight + selection */}
              <div className="pointer-events-none absolute left-[58%] top-[46%] h-10 w-24 -rotate-2 rounded-xl bg-violet-500/10 ring-1 ring-violet-400/20 cursorGlow" />
              <div className="pointer-events-none absolute left-[66%] top-[52%] h-3 w-3 rounded-full bg-white/70 shadow-[0_0_18px_rgba(255,255,255,0.35)]" />
            </div>

            {/* logs / terminal */}
            <div className="relative col-span-5 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div className="flex items-center justify-between">
                <div className="text-[13px] font-semibold text-white/70">Logs</div>
                <div className="text-[11px] text-white/35">autoscroll</div>
              </div>
              <TerminalChaos />
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-black/60 to-transparent" />
            </div>

            {/* error strip */}
            <div className="col-span-12 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3">
              <div className="flex items-center justify-between gap-3 text-[11px]">
                <div className="min-w-0 truncate text-red-200/90">
                  Error: orders rejected • "insufficient buying power" • retry queue growing…
                </div>
                <div className="whitespace-nowrap text-red-200/70">view stacktrace →</div>
              </div>
            </div>
          </div>

          {/* floating toasts inside left panel */}
          <Toast
            className="left-5 top-[86px]"
            tone="warn"
            title="Rate limit hit"
            body="Polygon: 429 — retrying in 15s"
          />
          <Toast
            className="right-5 top-[118px]"
            tone="bad"
            title="Auth expired"
            body="Broker token invalid — refresh failed"
          />
        </div>

        {/* right column: overlapping "windows" */}
        <div className="relative col-span-5">
          {/* Window 1: news */}
          <Window
            className="right-0 top-0 w-[94%] rotate-[2deg]"
            title="News feed"
            meta="last 30m"
            accent="violet"
          >
            <NewsLinesDense />
          </Window>

          {/* Window 2: spreadsheet */}
          <Window
            className="left-0 top-[38%] w-[98%] -rotate-[3deg]"
            title="Backtest spreadsheet"
            meta="manual edits"
            accent="emerald"
          >
            <SheetGridDense />
          </Window>

          {/* Window 3: broker docs / code */}
          <Window
            className="right-2 bottom-0 w-[90%] rotate-[1deg]"
            title="Broker docs"
            meta="auth + orders"
            accent="red"
          >
            <CodeBlockChaos />
          </Window>

          {/* sticky notes (extra chaos) */}
          <Sticky className="left-4 top-[18%] rotate-[-9deg]" text="remember to subtract fees" />
          <Sticky className="right-6 top-[62%] rotate-[7deg]" text="why is RSI NaN??" />

          {/* mini modal on top (API key expired) */}
          <div className="absolute left-1/2 top-[26%] z-20 w-[92%] -translate-x-1/2 rotate-[-1deg]">
            <div className="rounded-3xl border border-white/10 bg-black/55 p-4 backdrop-blur-xl shadow-[0_25px_90px_rgba(0,0,0,0.85)] glitch">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-white/80">API key expired</div>
                <div className="text-xs text-white/35">×</div>
              </div>
              <div className="mt-2 text-[11px] text-white/55">
                Alpaca rejected request: <span className="text-red-200/80">401 Unauthorized</span>
              </div>
              <div className="mt-3 flex items-center justify-between gap-2">
                <button className="flex-1 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-[11px] text-white/70">
                  Open dashboard
                </button>
                <button className="rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500 px-4 py-2 text-[11px] font-semibold text-white">
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* bottom row: tiny "open tabs" */}
        <div className="col-span-12 grid grid-cols-12 gap-4">
          <TinyTile title="Reddit sentiment" subtitle="WSB threads • +42%" />
          <TinyTile title="Macro data" subtitle="CPI • rates • DXY" />
          <TinyTile title="Earnings calendar" subtitle="surprises • guidance" />
          <TinyTile title="Risk controls" subtitle="stops • sizing • limits" />
        </div>
      </div>

      {/* outer vignette */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,0,0,0),rgba(0,0,0,0.86))]" />

      {/* local keyframes */}
      <style>{`
        .noise {
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E");
          animation: noiseMove 1.2s steps(2,end) infinite;
        }
        @keyframes noiseMove {
          0%{transform:translate3d(0,0,0)}
          50%{transform:translate3d(-8px,6px,0)}
          100%{transform:translate3d(0,0,0)}
        }

        .scanlines {
          background: repeating-linear-gradient(
            to bottom,
            rgba(255,255,255,0.05) 0px,
            rgba(255,255,255,0.05) 1px,
            rgba(0,0,0,0) 5px,
            rgba(0,0,0,0) 9px
          );
          animation: scan 6s linear infinite;
        }
        @keyframes scan {
          0%{transform:translateY(0)}
          100%{transform:translateY(40px)}
        }

        .glitch {
          animation: glitch 3.6s infinite;
        }
        @keyframes glitch {
          0%, 100% { transform: translateX(0) rotate(-1deg); }
          92% { transform: translateX(0) rotate(-1deg); }
          93% { transform: translateX(2px) rotate(-1deg); }
          94% { transform: translateX(-2px) rotate(-1deg); }
          95% { transform: translateX(1px) rotate(-1deg); }
          96% { transform: translateX(0) rotate(-1deg); }
        }

        .cursorGlow {
          animation: cursorPulse 2.2s ease-in-out infinite;
        }
        @keyframes cursorPulse {
          0%,100% { opacity: .35; }
          50% { opacity: .65; }
        }
      `}</style>
    </div>
  );
}

/* ------------------ little components ------------------ */

function Tab({ label, active }) {
  return (
    <div
      className={[
        "flex items-center gap-2 rounded-full px-3 py-1 text-[10px] whitespace-nowrap",
        active
          ? "bg-white/10 text-white/80 ring-1 ring-white/10"
          : "bg-white/[0.04] text-white/45 ring-1 ring-white/5",
      ].join(" ")}
    >
      <span className={active ? "text-violet-300/90" : "text-white/30"}>●</span>
      {label}
      <span className="ml-1 text-white/25">×</span>
    </div>
  );
}

function Pill({ label, value, tone }) {
  const toneCls =
    tone === "good"
      ? "text-emerald-200/90 border-emerald-400/20 bg-emerald-400/10"
      : tone === "warn"
      ? "text-yellow-200/90 border-yellow-400/20 bg-yellow-400/10"
      : tone === "bad"
      ? "text-red-200/90 border-red-400/20 bg-red-400/10"
      : "text-white/70 border-white/10 bg-white/5";

  return (
    <div className={`rounded-full border px-2 py-1 text-[10px] ${toneCls}`}>
      <span className="opacity-70">{label}:</span> <span className="font-semibold">{value}</span>
    </div>
  );
}

function Window({ className, title, meta, accent, children }) {
  const accentDot =
    accent === "violet"
      ? "bg-violet-400/70"
      : accent === "emerald"
      ? "bg-emerald-400/70"
      : "bg-red-400/70";

  return (
    <div
      className={[
        "absolute z-10 rounded-3xl border border-white/10 bg-black/35 p-4 backdrop-blur shadow-[0_20px_70px_rgba(0,0,0,0.78)]",
        className,
      ].join(" ")}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[11px] font-semibold text-white/70">
          <span className={`h-2 w-2 rounded-full ${accentDot}`} />
          {title}
        </div>
        <div className="text-[10px] text-white/40">{meta}</div>
      </div>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function Toast({ className, title, body, tone }) {
  const cls =
    tone === "warn"
      ? "border-yellow-400/20 bg-yellow-500/10 text-yellow-200/80"
      : "border-red-400/20 bg-red-500/10 text-red-200/80";

  return (
    <div
      className={[
        "absolute z-20 w-[220px] rounded-2xl border px-3 py-2 backdrop-blur shadow-[0_20px_70px_rgba(0,0,0,0.75)]",
        cls,
        className,
      ].join(" ")}
    >
      <div className="text-[10px] font-semibold">{title}</div>
      <div className="mt-1 text-[10px] opacity-80">{body}</div>
    </div>
  );
}

function Sticky({ className, text }) {
  return (
    <div
      className={[
        "absolute z-30 w-[140px] rounded-2xl border border-white/10 bg-white/10 px-3 py-3 text-[10px] text-white/70 backdrop-blur shadow-[0_18px_60px_rgba(0,0,0,0.8)]",
        className,
      ].join(" ")}
    >
      <div className="font-semibold text-white/75">note</div>
      <div className="mt-1 leading-snug opacity-80">{text}</div>
    </div>
  );
}

/* ------------------ faux "busy" content ------------------ */

function FakeChartSuperBusy() {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-black/30">
      <svg viewBox="0 0 520 180" className="h-[140px] w-full">
        <defs>
          <linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(16,185,129,0.32)" />
            <stop offset="100%" stopColor="rgba(16,185,129,0.00)" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* grid */}
        {Array.from({ length: 7 }).map((_, i) => (
          <line
            key={i}
            x1="0"
            x2="520"
            y1={18 + i * 22}
            y2={18 + i * 22}
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="1"
          />
        ))}
        {Array.from({ length: 8 }).map((_, i) => (
          <line
            key={i}
            y1="0"
            y2="180"
            x1={i * 74}
            x2={i * 74}
            stroke="rgba(255,255,255,0.04)"
            strokeWidth="1"
          />
        ))}

        {/* area */}
        <path
          d="M0 132 L24 120 L48 138 L72 112 L96 118 L120 92 L144 104 L168 78 L192 86 L216 64 L240 74 L264 56 L288 60 L312 44 L336 62 L360 38 L384 55 L408 34 L432 48 L456 30 L480 44 L520 26 L520 180 L0 180 Z"
          fill="url(#ag)"
        />
        {/* line */}
        <path
          d="M0 132 L24 120 L48 138 L72 112 L96 118 L120 92 L144 104 L168 78 L192 86 L216 64 L240 74 L264 56 L288 60 L312 44 L336 62 L360 38 L384 55 L408 34 L432 48 L456 30 L480 44 L520 26"
          fill="none"
          stroke="rgba(16,185,129,0.95)"
          strokeWidth="3"
          filter="url(#glow)"
        />

        {/* overlays: indicators */}
        <path
          d="M0 90 L60 92 L120 88 L180 94 L240 86 L300 92 L360 84 L420 90 L520 86"
          stroke="rgba(168,85,247,0.65)"
          strokeWidth="2"
          fill="none"
          strokeDasharray="4 4"
        />
        <path
          d="M0 70 L70 74 L140 68 L210 72 L280 66 L350 70 L420 64 L520 68"
          stroke="rgba(255,255,255,0.25)"
          strokeWidth="2"
          fill="none"
        />

        {/* markers */}
        {[72, 168, 312, 456].map((x, idx) => (
          <circle
            key={x}
            cx={x}
            cy={[112, 78, 44, 30][idx]}
            r="4"
            fill="rgba(255,255,255,0.55)"
          />
        ))}
      </svg>

      <div className="flex items-center justify-between px-3 py-2 text-[10px] text-white/45">
        <span>entries: 14</span>
        <span>exits: 13</span>
        <span>fees: on</span>
        <span>slip: 0.02%</span>
      </div>
    </div>
  );
}

function TerminalChaos() {
  const lines = [
    ["[fetch]", "polygon: AAPL 1D (2000 bars)"],
    ["[calc]", "rsi(14)=29.7 → oversold"],
    ["[signal]", "enter_long=true"],
    ["[risk]", "stop=-1.0% take=2.2% size=0.12"],
    ["[sim]", "fill @ 191.24 (paper)"],
    ["[warn]", "missing holiday bar → forward-fill"],
    ["[opt]", "gridsearch: rsi=12..18, stop=0.7..1.4"],
    ["[err]", "order rejected: insufficient buying power"],
    ["[retry]", "enqueue order → backoff 2s"],
    ["[err]", "broker 401 → refresh token failed"],
    ["[retry]", "rotate API key → rate limited"],
    ["[done]", "sharpe=1.12 dd=-8.4% trades=92"],
  ];

  return (
    <div className="mt-2 space-y-1 font-mono text-[10px] leading-snug">
      {lines.map((l, i) => (
        <div key={i} className="flex gap-2">
          <span className="text-white/25">{String(i + 1).padStart(2, "0")}</span>
          <span className={tagColor(l[0])}>{l[0]}</span>
          <span className={msgColor(l[0])}>{l[1]}</span>
        </div>
      ))}
      <div className="mt-2 h-px bg-white/10" />
      <div className="text-white/35">
        › run_backtest(strategy="mean_reversion", symbol="AAPL")<span className="ml-1 inline-block h-[10px] w-[2px] bg-white/50 align-middle animate-pulse" />
      </div>
    </div>
  );
}

function tagColor(tag) {
  if (tag === "[err]") return "text-red-200/85";
  if (tag === "[warn]") return "text-yellow-200/85";
  if (tag === "[done]") return "text-emerald-200/85";
  return "text-white/55";
}
function msgColor(tag) {
  if (tag === "[err]") return "text-red-200/70";
  if (tag === "[warn]") return "text-yellow-200/70";
  if (tag === "[done]") return "text-emerald-200/70";
  return "text-white/55";
}

function NewsLinesDense() {
  const rows = [
    ["Fed speaker hints higher-for-longer", "Macro"],
    ["AAPL supplier reports demand softness", "Earnings"],
    ["Options flow spikes in TSLA calls", "Flow"],
    ["WSB mentions: GME +42% (1h)", "Social"],
    ["Oil pops on geopolitics headlines", "Macro"],
    ["Tech sells off into close", "Tape"],
  ];

  return (
    <div className="space-y-2">
      {rows.map(([t, s], i) => (
        <div
          key={i}
          className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/[0.04] px-3 py-2"
        >
          <div className="min-w-0 truncate text-[10px] text-white/65">{t}</div>
          <div className="whitespace-nowrap rounded-full border border-white/10 bg-black/30 px-2 py-1 text-[9px] text-white/45">
            {s}
          </div>
        </div>
      ))}
    </div>
  );
}

function SheetGridDense() {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04]">
      <div className="grid grid-cols-8 gap-px bg-white/10 p-px">
        {Array.from({ length: 8 * 8 }).map((_, idx) => {
          const hot = [10, 11, 12, 18, 19, 27, 36, 44, 52].includes(idx);
          const warn = [22, 23, 31, 39].includes(idx);
          return (
            <div
              key={idx}
              className={[
                "h-6 bg-black/30",
                hot ? "bg-emerald-400/15 ring-1 ring-emerald-400/20" : "",
                warn ? "bg-yellow-400/15 ring-1 ring-yellow-400/20" : "",
              ].join(" ")}
            />
          );
        })}
      </div>
      <div className="flex items-center justify-between px-3 py-2 text-[10px] text-white/45">
        <span>tickers: 18</span>
        <span>rules: 6</span>
        <span>copy/paste: nonstop</span>
      </div>
    </div>
  );
}

function CodeBlockChaos() {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-black/30">
      <div className="flex items-center justify-between border-b border-white/10 bg-white/[0.04] px-3 py-2">
        <div className="text-[10px] font-semibold text-white/60">POST /v2/orders</div>
        <div className="text-[10px] text-white/35">Authorization: Bearer …</div>
      </div>

      <pre className="p-3 text-[10px] leading-snug text-white/55">
{`{
  "symbol": "AAPL",
  "side": "buy",
  "type": "market",
  "time_in_force": "day",
  "qty": 2,
  "client_order_id": "mobius_8f2a",
  "extended_hours": true
}`}
      </pre>

      <div className="border-t border-white/10 px-3 py-2 text-[10px] text-white/40">
        401 → refresh token → retry → 429 → backoff → retry…
      </div>
    </div>
  );
}

function TinyTile({ title, subtitle }) {
  // Different visualization based on title
  const renderContent = () => {
    if (title === "Reddit sentiment") {
      return (
        <div className="mt-3 space-y-1.5">
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">Positive</span>
            <span className="text-green-400 font-mono">42%</span>
          </div>
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-green-400/60 rounded-full" style={{width: '42%'}} />
          </div>
          <div className="flex gap-1.5 mt-2">
            <span className="bg-green-500/20 rounded px-2 py-1 text-[9px] text-green-300">TSLA</span>
            <span className="bg-purple-500/20 rounded px-2 py-1 text-[9px] text-purple-300">GME</span>
            <span className="bg-blue-500/20 rounded px-2 py-1 text-[9px] text-blue-300">NVDA</span>
          </div>
        </div>
      );
    }

    if (title === "Macro data") {
      return (
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">CPI</span>
            <span className="text-red-400 font-mono">+3.2%</span>
          </div>
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">Fed</span>
            <span className="text-white/70 font-mono">5.25%</span>
          </div>
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">DXY</span>
            <span className="text-green-400 font-mono">103.2</span>
          </div>
        </div>
      );
    }

    if (title === "Earnings calendar") {
      return (
        <div className="mt-3 space-y-1.5">
          <div className="bg-white/5 rounded-lg px-2.5 py-2">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-white/70 font-semibold">NVDA</span>
              <span className="text-white/50">Today 4PM</span>
            </div>
            <div className="text-[9px] text-white/40 mt-0.5">EPS Est: $4.52</div>
          </div>
          <div className="bg-yellow-500/10 rounded px-2 py-1 text-[9px] text-yellow-300/80">
            ⚠ High volatility
          </div>
        </div>
      );
    }

    if (title === "Risk controls") {
      return (
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">Stop Loss</span>
            <span className="text-red-300 font-mono">-2.5%</span>
          </div>
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">Position</span>
            <span className="text-white/70 font-mono">5% max</span>
          </div>
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-white/40">Daily Limit</span>
            <span className="text-emerald-300 font-mono">3 trades</span>
          </div>
        </div>
      );
    }

    return <div className="mt-3 h-10 rounded-2xl bg-white/5" />;
  };

  return (
    <div className="col-span-3 rounded-3xl border border-white/10 bg-white/[0.04] p-5 backdrop-blur">
      <div className="text-[13px] font-semibold text-white/75">{title}</div>
      <div className="mt-1 text-[11px] text-white/45">{subtitle}</div>
      {renderContent()}
    </div>
  );
}
