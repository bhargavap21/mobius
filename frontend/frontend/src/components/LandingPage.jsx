import { useState, lazy, Suspense, useMemo } from 'react'
import { SiX, SiReddit, SiYoutube } from 'react-icons/si'
import { useNavigate } from 'react-router-dom'
import Login from './Login'
import Signup from './Signup'
import StrategyCarousel from './StrategyCarousel'
import { ManualWorkflowMockChaos } from './ManualWorkflowMockChaos'

const ObservabilityGraph = lazy(() => import('./ObservabilityGraph'))

export default function LandingPage({ onGetStarted, onShowSignup, user, onSignOut, onShowBotLibrary }) {
  const navigate = useNavigate()
  const isAuthenticated = !!user
  const [showLogin, setShowLogin] = useState(false)
  const [showSignup, setShowSignup] = useState(false)
  const [email, setEmail] = useState('')

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleBuildBot = () => {
    // Always navigate to dashboard
    onGetStarted?.()
  }

  const handleGetStarted = () => {
    // Navigate to get-started page (for navbar and "Stop guessing" section)
    navigate('/get-started')
  }

  const handleHeroGetStarted = () => {
    // Hero section Get Started does nothing for now
    if (email) {
      localStorage.setItem('userEmail', email)
    }
  }

  return (
    <div className="w-full bg-black">
      {/* Navbar */}
      <div className="sticky top-0 z-50 bg-dark-surface/50 backdrop-blur-sm">
        <div className="w-full px-6 py-6 flex items-center justify-between">
          {/* Left: Logo and Brand */}
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="flex items-center gap-4 text-white hover:opacity-80 transition-opacity"
          >
            <img
              src="/logo.png"
              alt="Mobius Logo"
              className="h-16 w-16 brightness-125"
            />
            <span className="text-3xl font-light">Mobius</span>
          </button>

          {/* Right: Get Started Button */}
          <button
            onClick={handleGetStarted}
            className="relative px-6 py-2.5 bg-gradient-to-br from-violet-600 via-violet-500 to-purple-600 text-white text-sm font-semibold rounded-full hover:scale-[1.02] transition-all shadow-lg shadow-violet-500/50 overflow-hidden group"
          >
            {/* Glossy overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/20 via-transparent to-transparent rounded-full pointer-events-none" />
            {/* Bottom shine */}
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/10 to-transparent rounded-full pointer-events-none" />
            <span className="relative">Get Started</span>
          </button>
        </div>
      </div>

      {/* Hero Section with 3D */}
      <section className="w-full h-screen overflow-hidden relative bg-black">
        {/* Purple backdrop */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          {/* left big blob */}
          <div className="absolute -left-40 top-24 h-[520px] w-[520px] rounded-full
                          bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.55),transparent_60%)]
                          blur-3xl opacity-70" />

          {/* center soft sweep */}
          <div className="absolute left-1/2 top-0 h-[700px] w-[700px] -translate-x-1/2
                          rounded-full bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.35),transparent_65%)]
                          blur-3xl opacity-60" />

          {/* right arc-ish blob */}
          <div className="absolute right-[-220px] top-[-120px] h-[720px] w-[720px]
                          rounded-full bg-[conic-gradient(from_180deg,rgba(168,85,247,0.0),rgba(168,85,247,0.55),rgba(168,85,247,0.0))]
                          blur-3xl opacity-60" />
        </div>
        <div className="max-w-7xl mx-auto h-full px-6 flex items-center">
          {/* Left side - Text */}
          <div className="w-1/2 z-10" style={{ isolation: 'isolate', willChange: 'transform', transform: 'translateZ(0)' }}>
            <h1 className="text-6xl md:text-7xl font-light text-white mb-8 leading-tight whitespace-nowrap">
              Your AI Trading Desk
            </h1>
            <p className="text-2xl md:text-3xl lg:text-4xl text-gray-400 leading-relaxed mb-12">
              AI That Turns Ideas Into Trades
            </p>
            <div className="flex items-center gap-0 max-w-3xl bg-gradient-to-r from-purple-900/20 to-blue-900/20 backdrop-blur-sm rounded-2xl p-2 border border-purple-500/20">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleHeroGetStarted()}
                placeholder="Your Email Address"
                className="flex-1 px-8 py-6 bg-transparent text-white placeholder-gray-400 outline-none text-xl"
              />
              <button
                onClick={handleHeroGetStarted}
                className="px-10 py-6 bg-white text-black text-xl font-semibold rounded-xl hover:bg-gray-100 transition-all whitespace-nowrap"
              >
                Get Started
              </button>
            </div>

            {/* Platform Integrations */}
            <div className="mt-20">
              <p className="text-base text-gray-500 mb-10 text-center tracking-wide">
                Connects to the tools you already use
              </p>
              <div className="flex flex-wrap items-center justify-center gap-x-16 gap-y-8">
                <span className="text-white text-3xl font-semibold opacity-60 hover:opacity-100 transition-opacity">
                  Alpaca
                </span>
                <span className="text-white text-3xl font-bold opacity-60 hover:opacity-100 transition-opacity tracking-tight">
                  IBKR
                </span>
                <span className="text-white text-3xl font-semibold opacity-60 hover:opacity-100 transition-opacity">
                  Tradier
                </span>
                <span className="text-white text-3xl font-semibold opacity-60 hover:opacity-100 transition-opacity">
                  Polygon
                </span>
                <span className="text-white text-3xl font-semibold opacity-60 hover:opacity-100 transition-opacity">
                  Finnhub
                </span>
                <span className="text-white text-3xl font-bold opacity-60 hover:opacity-100 transition-opacity" style={{ fontFamily: 'Georgia, serif' }}>
                  Y! Finance
                </span>
              </div>
            </div>
          </div>

          {/* Right side - 3D Logo */}
          <div className="w-1/2 h-full absolute right-[-20rem] top-0 flex items-start justify-center pointer-events-none overflow-hidden" style={{ isolation: 'isolate' }}>
            <div className="w-full h-full flex items-center justify-center overflow-hidden relative">
              <iframe
                src='https://my.spline.design/mobiusmiamisunsetcopy-SKOxlmvEV8x6vDuzNWCJ8AFf/'
                width='100%'
                height='100%'
                title="Mobius 3D Logo"
                style={{ border: 'none', pointerEvents: 'none', background: 'transparent' }}
              />
              {/* Transparent overlay to block scroll interactions */}
              <div className="absolute inset-0 pointer-events-auto" style={{ background: 'transparent' }} />
            </div>
          </div>
        </div>

      </section>

      {/* Strategy Carousel - Full Width */}
      <div className="relative w-full bg-black -mt-32 pb-12">
        <StrategyCarousel />
      </div>

      {/* Without Mobius Section */}
      <section id="process" className="relative overflow-hidden bg-black py-20">
        {/* subtle purple haze */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-[-260px] h-[700px] w-[700px] -translate-x-1/2 rounded-full
                          bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.22),transparent_60%)]
                          blur-3xl opacity-70" />
          <div className="absolute left-[10%] top-[30%] h-[520px] w-[520px] rounded-full
                          bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.16),transparent_65%)]
                          blur-3xl opacity-60" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          <div className="text-center">
            <h2 className="text-4xl md:text-6xl font-light tracking-tight text-white">
              Without Mobius, <span className="italic font-light !text-violet-400">it's chaos.</span>
            </h2>

            <p className="mx-auto mt-3 max-w-2xl text-base md:text-lg text-white/60">
              Tabs, spreadsheets, signals, docs—stitched together by vibes.
            </p>
          </div>

          {/* The chaos visualization */}
          <div className="relative mt-14 mx-auto h-[620px] max-w-6xl overflow-hidden">
            {/* vignette */}
            <div className="pointer-events-none absolute inset-0 rounded-[40px]
                            bg-[radial-gradient(ellipse_at_center,rgba(0,0,0,0),rgba(0,0,0,0.85))]
                            ring-1 ring-white/10" />

            {/* center "confusion core" */}
            <div className="
              absolute inset-0
              rounded-[40px]
              overflow-hidden
            ">
              <ManualWorkflowMockChaos />
            </div>

            {/* overlapping floating tabs */}
            <div className="absolute inset-0 pointer-events-none">
              <FloatingTab label="Reddit sentiment" sub="WSB threads" position="top-12 left-8" rotate="-3deg" data={{ type: 'sentiment' }} />
              <FloatingTab label="News feed" sub="headlines" position="top-8 right-12" rotate="2deg" data={{ type: 'news' }} />
              <FloatingTab label="Macro data" sub="rates / CPI" position="bottom-32 left-16" rotate="4deg" data={{ type: 'macro' }} />
              <FloatingTab label="Earnings calendar" sub="surprises" position="bottom-24 right-8" rotate="-2deg" data={{ type: 'earnings' }} />
              <FloatingTab label="Backtest spreadsheet" sub="manual" position="top-1/3 left-4" rotate="-5deg" data={{ type: 'backtest' }} />
              <FloatingTab label="Broker docs" sub="API + auth" position="top-1/2 right-6" rotate="3deg" data={{ type: 'docs' }} />
            </div>
          </div>

          {/* With Mobius section - Omen-style with grainy particle mesh */}
          <div className="mt-24">
            {/* header */}
            <div className="text-center">
              <h2 className="text-4xl md:text-6xl font-light tracking-tight text-white">
                With Mobius, <span className="italic !text-violet-400">it's effortless.</span>
              </h2>
              <p className="mx-auto mt-3 max-w-2xl text-base md:text-lg text-white/60">
                Stream signals in. Get deployable code out.
              </p>
            </div>

            {/* BIG visual panel */}
            <div className="relative mt-14 overflow-hidden rounded-[44px] border border-white/10 bg-black shadow-[0_40px_140px_rgba(0,0,0,0.88)]">

              {/* panel haze + vignette + film grain */}
              <div aria-hidden="true" className="pointer-events-none absolute inset-0">
                <div className="absolute left-[-320px] top-[-360px] h-[980px] w-[980px] rounded-full bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.20),transparent_60%)] blur-3xl opacity-90" />
                <div className="absolute right-[-420px] top-[-320px] h-[1120px] w-[1120px] rounded-full bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.22),transparent_62%)] blur-3xl opacity-80" />
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,0,0,0),rgba(0,0,0,0.92))]" />
                {/* subtle film grain */}
                <div className="absolute inset-0 opacity-[0.10] mix-blend-overlay filmgrain" />
              </div>

              <div className="relative grid min-h-[420px] grid-cols-12">
                {/* LEFT: sophisticated chart + grainy particle mesh */}
                <div className="relative col-span-12 md:col-span-8">
                  <MarketLikeEquityCurve />
                  <LogoColoredGrainFlow />
                  <LogoStream />

                  {/* edge fades */}
                  <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-black to-transparent z-40" />
                  <div className="pointer-events-none absolute inset-y-0 right-0 w-20 bg-gradient-to-l from-black/80 to-transparent z-40" />
                </div>

                {/* RIGHT: realistic trading computer with phone-like angle */}
                <div className="relative col-span-12 md:col-span-4">
                  <div className="absolute right-[-10px] top-1/2 z-40 -translate-y-1/2">
                    <div className="[transform-style:preserve-3d] [transform:perspective(1400px)_rotateY(-24deg)_rotateX(6deg)_rotateZ(2deg)]">
                      <AngledLaptop>
                        <ComputerRealisticTradingScreen />
                      </AngledLaptop>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        <style>{`
          @keyframes orbit {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          @keyframes float {
            0%,100% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
          }

          /* film grain */
          .filmgrain {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
            animation: grain 1.4s steps(2,end) infinite;
          }
          @keyframes grain {
            0% { transform: translate3d(0,0,0); }
            30% { transform: translate3d(-6px,4px,0); }
            60% { transform: translate3d(5px,-3px,0); }
            100% { transform: translate3d(0,0,0); }
          }

          /* logos ride along the mesh path */
          .logoRide {
            offset-path: path("M120 298 C 230 250, 330 340, 450 304 C 550 274, 620 332, 720 296 C 800 270, 850 280, 910 258");
            -webkit-offset-path: path("M120 298 C 230 250, 330 340, 450 304 C 550 274, 620 332, 720 296 C 800 270, 850 280, 910 258");
            offset-rotate: 0deg;
            animation: ride 5.2s linear infinite;
            will-change: offset-distance, transform, opacity;
          }
          @keyframes ride {
            0% { offset-distance: 0%; opacity: 0; transform: scale(0.92); }
            10% { opacity: 1; }
            86% { opacity: 1; }
            100% { offset-distance: 100%; opacity: 0; transform: scale(0.92); }
          }

          @keyframes shimmer {
            from { transform: translateX(-320px); }
            to { transform: translateX(920px); }
          }
        `}</style>
      </section>

      {/* Features Section */}
      <section className="relative bg-black py-24 overflow-hidden">
        {/* Aurora blobs + vignette + grain */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-40 left-[-10%] h-[520px] w-[520px] rounded-full bg-violet-600/20 blur-[120px]" />
          <div className="absolute top-10 right-[-10%] h-[520px] w-[520px] rounded-full bg-emerald-500/18 blur-[140px]" />
          <div className="absolute bottom-[-220px] left-[30%] h-[620px] w-[620px] rounded-full bg-fuchsia-500/10 blur-[160px]" />
          {/* Vignette */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_40%,rgba(0,0,0,0.85)_78%)]" />
          {/* CSS grain */}
          <div className="absolute inset-0 opacity-[0.08] mix-blend-overlay bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22><filter id=%22n%22 x=%220%22 y=%220%22><feTurbulence type=%22fractalNoise%22 baseFrequency=%220.9%22 numOctaves=%223%22 stitchTiles=%22stitch%22/></filter><rect width=%22120%22 height=%22120%22 filter=%22url(%23n)%22 opacity=%220.55%22/></svg>')]" />
        </div>

        <div className="relative mx-auto max-w-6xl px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-tight text-white">
              Powerful Features
            </h2>
            <p className="mt-4 text-base text-white/60 max-w-2xl mx-auto">
              Everything you need to build, test, and deploy trading strategies
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* From Idea to Bot */}
            <div className="group relative rounded-3xl border border-white/10 bg-white/[0.02] p-8 backdrop-blur-xl overflow-hidden">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.08),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative">
                <h3 className="text-xl font-light text-white/90">From idea to bot</h3>
                <p className="mt-2 text-sm text-white/45">Plain English → production code in seconds</p>

                <MicroStrategyScreen />
              </div>
            </div>

            {/* Backtest to Code */}
            <div className="group relative rounded-3xl border border-white/10 bg-white/[0.02] p-8 backdrop-blur-xl overflow-hidden">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(16,185,129,0.08),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative">
                <h3 className="text-xl font-light text-white/90">Backtest to code</h3>
                <p className="mt-2 text-sm text-white/45">Instant validation with real market data</p>

                <MicroBacktestScreen />
              </div>
            </div>

            {/* Live signal feed */}
            <div className="group relative rounded-3xl border border-white/10 bg-white/[0.02] p-8 backdrop-blur-xl overflow-hidden">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(59,130,246,0.08),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative">
                <h3 className="text-xl font-light text-white/90">Live signal feed</h3>
                <p className="mt-2 text-sm text-white/45">News, sentiment, macro — all in one stream</p>

                <MicroFeedScreen />
              </div>
            </div>

            {/* Risk monitoring */}
            <div className="group relative rounded-3xl border border-white/10 bg-white/[0.02] p-8 backdrop-blur-xl overflow-hidden">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(239,68,68,0.06),transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative">
                <h3 className="text-xl font-light text-white/90">Risk monitoring</h3>
                <p className="mt-2 text-sm text-white/45">Real-time alerts before limits break</p>

                <MicroRiskScreen />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Comparison Graph */}
      <section className="bg-black py-16 px-6">
        <Suspense fallback={
          <div className="h-96 flex items-center justify-center text-white/40">
            Loading chart...
          </div>
        }>
          <ObservabilityGraph />
        </Suspense>
      </section>

      {/* Portfolio CTA Section */}
      <section className="relative bg-black py-32 overflow-hidden">
        {/* Aurora backdrop */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          <div className="absolute left-[-15%] top-[-20%] h-[700px] w-[700px] rounded-full bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.28),transparent_65%)] blur-3xl opacity-80" />
          <div className="absolute right-[-10%] bottom-[-25%] h-[800px] w-[800px] rounded-full bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.20),transparent_60%)] blur-3xl opacity-75" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left: Content */}
            <div>
              <h2 className="text-5xl md:text-6xl lg:text-7xl font-light tracking-tight text-white leading-tight">
                Stop guessing.<br />Start testing.
              </h2>
              <p className="mt-6 text-xl text-white/60 max-w-lg">
                Backtest any thesis and ship a broker-ready bot—no code required.
              </p>
              <button
                onClick={handleGetStarted}
                className="mt-8 group relative inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-violet-600 to-violet-500 px-8 py-4 text-lg font-medium text-white shadow-lg shadow-violet-500/25 transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-violet-500/40"
              >
                Get started
                <svg className="h-5 w-5 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>

            {/* Right: Laptop Image */}
            <div className="relative lg:pl-8">
              <div className="relative">
                <img
                  src="/laptop.png"
                  alt="Trading platform interface"
                  className="w-full h-auto"
                />
                {/* Glow effect */}
                <div className="absolute inset-0 -z-10 rounded-3xl bg-gradient-to-br from-violet-500/30 to-emerald-500/20 blur-3xl" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black border-t border-white/5 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-start gap-8 pb-8 border-b border-white/5">
            {/* Legal Links */}
            <div className="flex flex-wrap gap-6">
              <a href="#" className="text-sm text-white/60 hover:text-white/90 transition-colors">About</a>
              <a href="#" className="text-sm text-white/60 hover:text-white/90 transition-colors">Legal Documents & Disclosures</a>
            </div>
          </div>

          {/* Disclaimer Text */}
          <div className="grid md:grid-cols-3 gap-8 pt-8 text-xs text-white/40 leading-relaxed">
            <div>
              <p>
                Mobius ("Mobius") is an AI-powered trading platform that provides algorithmic trading tools to US residents. By using this website, you accept our Terms of Use and Privacy Policy and other disclosures as described in Legal Documents & Disclosures. Mobius's AI advisory services are available only to residents of the United States in jurisdictions where Mobius is registered. Nothing on this website should be considered an offer, solicitation of an offer, or advice to buy or sell securities.
              </p>
            </div>
            <div>
              <p>
                Past performance is no guarantee of future results. Any historical returns, expected returns or probability projections are hypothetical in nature and may not reflect actual future performance. Account holdings are for illustrative purposes only and are not investment recommendations. Registration with the SEC does not imply a certain level of skill or training.
              </p>
            </div>
            <div>
              <p>
                Brokerage services are provided to Mobius Clients by Alpaca, an SEC registered broker-dealer and member FINRA/SIPC. For more information, see our Legal Documents & Disclosures. Contact: team@joinmobius.com. For all information or inquiries regarding Mobius's Custodian, Alpaca Securities LLC, please visit: https://alpaca.markets/.
              </p>
            </div>
          </div>
        </div>
      </footer>

      {/* Login/Signup Modals */}
      {showLogin && (
        <Login
          onClose={() => setShowLogin(false)}
          onSwitchToSignup={() => {
            setShowLogin(false)
            setShowSignup(true)
          }}
          onSuccess={() => {
            setShowLogin(false)
            onGetStarted?.()
          }}
        />
      )}
      {showSignup && (
        <Signup
          onClose={() => setShowSignup(false)}
          onSwitchToLogin={() => {
            setShowSignup(false)
            setShowLogin(false)
          }}
        />
      )}
    </div>
  )
}

// Floating Tab Component
function FloatingTab({ label, sub, position, rotate }) {
  return (
    <div
      className={`absolute ${position} pointer-events-auto`}
      style={{
        transform: `rotate(${rotate})`,
        animation: 'float 6s ease-in-out infinite'
      }}
    >
      <div className="rounded-xl border border-white/20 bg-gray-900/90 backdrop-blur-md px-4 py-3 shadow-2xl min-w-[160px]">
        <div className="flex items-center gap-2 mb-1">
          <div className="h-2 w-2 rounded-full bg-violet-400 animate-pulse" />
          <p className="text-xs font-medium text-white/90">{label}</p>
        </div>
        <p className="text-[10px] text-white/50">{sub}</p>
      </div>
    </div>
  )
}

// All the micro-screen components and visual components
function MicroStrategyScreen() {
  return (
    <div className="relative mt-5 overflow-hidden rounded-2xl border border-white/10 bg-black/35">
      {/* Browser window dots */}
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-3 py-2">
        <span className="h-2 w-2 rounded-full bg-red-400/70" />
        <span className="h-2 w-2 rounded-full bg-yellow-400/60" />
        <span className="h-2 w-2 rounded-full bg-emerald-400/60" />
        <div className="ml-2 text-[11px] text-white/55">Strategy prompt</div>
      </div>

      {/* Prompt input */}
      <div className="p-4 border-b border-white/5">
        <div className="flex items-start gap-2">
          <div className="mt-1 h-2 w-2 rounded-full bg-violet-400" />
          <p className="text-sm text-white/70 leading-relaxed">
            Buy AAPL when RSI &lt; 30 and volume spikes above 20-day average
          </p>
        </div>
      </div>

      {/* "Compiler" output */}
      <div className="p-4 font-mono text-xs">
        <div className="space-y-1">
          <div className="flex gap-2">
            <span className="text-violet-400">def</span>
            <span className="text-emerald-300">strategy</span>
            <span className="text-white/60">(data):</span>
          </div>
          <div className="pl-4 text-white/50">
            rsi = calc_rsi(data, 14)
          </div>
          <div className="pl-4 text-white/50">
            vol_avg = data['volume'].rolling(20).mean()
          </div>
          <div className="pl-4 flex gap-2">
            <span className="text-violet-400">if</span>
            <span className="text-white/60">rsi &lt; 30 and vol &gt; vol_avg:</span>
          </div>
          <div className="pl-8 flex gap-2">
            <span className="text-violet-400">return</span>
            <span className="text-emerald-300">'BUY'</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function MicroBacktestScreen() {
  // Generate simple sparkline path
  const sparkline = useMemo(() => {
    const points = Array.from({ length: 20 }, (_, i) => {
      const x = (i / 19) * 100
      const y = 50 + Math.sin(i * 0.5) * 20 + (i * 1.5)
      return `${x},${y}`
    })
    return `M ${points.join(' L ')}`
  }, [])

  return (
    <div className="relative mt-5 overflow-hidden rounded-2xl border border-white/10 bg-black/35">
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-3 py-2">
        <span className="h-2 w-2 rounded-full bg-red-400/70" />
        <span className="h-2 w-2 rounded-full bg-yellow-400/60" />
        <span className="h-2 w-2 rounded-full bg-emerald-400/60" />
        <div className="ml-2 text-[11px] text-white/55">Backtest results</div>
      </div>

      <div className="p-4">
        {/* Chart */}
        <svg className="w-full h-24 mb-3" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <linearGradient id="microGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgb(16, 185, 129)" stopOpacity="0.2" />
              <stop offset="100%" stopColor="rgb(16, 185, 129)" stopOpacity="0" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <path d={`${sparkline} L 100,100 L 0,100 Z`} fill="url(#microGrad)" />
          <path d={sparkline} fill="none" stroke="rgb(16, 185, 129)" strokeWidth="0.8" filter="url(#glow)" />
        </svg>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <p className="text-white/40 mb-0.5">Return</p>
            <p className="text-emerald-400 font-medium">+64.2%</p>
          </div>
          <div>
            <p className="text-white/40 mb-0.5">Win Rate</p>
            <p className="text-white/80 font-medium">58%</p>
          </div>
          <div>
            <p className="text-white/40 mb-0.5">Sharpe</p>
            <p className="text-white/80 font-medium">1.84</p>
          </div>
          <div>
            <p className="text-white/40 mb-0.5">Max DD</p>
            <p className="text-red-400/80 font-medium">-12.4%</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function MicroFeedScreen() {
  const feeds = [
    { symbol: 'AAPL', reasoning: 'Bullish crossover + earnings beat', sentiment: 'pos' },
    { symbol: 'TSLA', reasoning: 'High vol + news catalyst detected', sentiment: 'pos' },
    { symbol: 'NVDA', reasoning: 'RSI oversold, mean reversion play', sentiment: 'neu' },
  ]

  return (
    <div className="relative mt-5 overflow-hidden rounded-2xl border border-white/10 bg-black/35">
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-3 py-2">
        <span className="h-2 w-2 rounded-full bg-red-400/70" />
        <span className="h-2 w-2 rounded-full bg-yellow-400/60" />
        <span className="h-2 w-2 rounded-full bg-emerald-400/60" />
        <div className="ml-2 text-[11px] text-white/55">Live feed</div>
      </div>

      <div className="p-4 space-y-3">
        {feeds.map((item, i) => (
          <div key={i} className="flex items-start gap-3 pb-3 border-b border-white/5 last:border-0">
            <div className={`mt-0.5 h-1.5 w-1.5 rounded-full ${
              item.sentiment === 'pos' ? 'bg-emerald-400' :
              item.sentiment === 'neg' ? 'bg-red-400' : 'bg-gray-400'
            }`} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white/90 mb-1">{item.symbol}</p>
              <p className="text-xs text-white/50 leading-relaxed">{item.reasoning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function MicroRiskScreen() {
  return (
    <div className="relative mt-5 overflow-hidden rounded-2xl border border-white/10 bg-black/35">
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-3 py-2">
        <span className="h-2 w-2 rounded-full bg-red-400/70" />
        <span className="h-2 w-2 rounded-full bg-yellow-400/60" />
        <span className="h-2 w-2 rounded-full bg-emerald-400/60" />
        <div className="ml-2 text-[11px] text-white/55">Risk dashboard</div>
      </div>

      <div className="p-4 space-y-4">
        {/* Portfolio exposure */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs text-white/60">Portfolio Exposure</p>
            <p className="text-xs text-white/90 font-medium">72%</p>
          </div>
          <div className="relative h-2 w-full overflow-hidden rounded-full bg-white/5">
            <div
              className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-emerald-500/80 to-yellow-500/80"
              style={{ width: '72%', animation: 'fillBar 2s ease-out' }}
            />
          </div>
        </div>

        {/* VaR */}
        <div className="flex items-center justify-between py-2 border-b border-white/5">
          <p className="text-xs text-white/60">Value at Risk (95%)</p>
          <p className="text-xs text-white/90 font-medium">$4,230</p>
        </div>

        {/* Beta */}
        <div className="flex items-center justify-between py-2 border-b border-white/5">
          <p className="text-xs text-white/60">Portfolio Beta</p>
          <p className="text-xs text-white/90 font-medium">1.23</p>
        </div>

        {/* Alert */}
        <div className="flex items-start gap-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 px-3 py-2">
          <svg className="mt-0.5 h-3 w-3 text-yellow-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <p className="text-[10px] text-yellow-200/90 leading-relaxed">
            Approaching max drawdown threshold
          </p>
        </div>
      </div>

      <style>{`
        @keyframes fillBar {
          from { width: 0%; }
        }
      `}</style>
    </div>
  )
}

// With Mobius visual components
function MarketLikeEquityCurve() {
  const path = useMemo(() => {
    // Seeded random for determinism
    const rand = (i, offset = 0) => {
      const x = Math.sin(i * 12.9898 + offset * 78.233) * 43758.5453
      return x - Math.floor(x)
    }

    const pts = []
    let base = 210

    for (let i = 0; i < 260; i++) {
      const x = 60 + i * 3.2
      const t = i / 260

      // Volatility clusters
      const vol = 1.6 + 2.2 * Math.sin(t * Math.PI * 2.4) ** 2

      // Micro-wiggles
      const noise = (rand(i, 1) - 0.5) * vol * 10

      // Occasional spikes
      const spike = rand(i, 9) > 0.988 ? (rand(i, 13) - 0.5) * 26 : 0

      // Slow upward trend
      const trend = t * 80

      base += noise + spike * 0.7
      base = Math.max(140, Math.min(340, base))

      const y = base - trend
      pts.push(`${x},${y}`)
    }

    return `M ${pts.join(' L ')}`
  }, [])

  return (
    <div className="absolute inset-0 flex items-center justify-center opacity-50">
      <svg
        viewBox="0 0 900 420"
        className="h-full w-auto"
        style={{ filter: 'blur(0.5px)' }}
      >
        <defs>
          <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgb(16,185,129)" stopOpacity="0.35" />
            <stop offset="60%" stopColor="rgb(16,185,129)" stopOpacity="0.15" />
            <stop offset="100%" stopColor="rgb(16,185,129)" stopOpacity="0" />
          </linearGradient>
          <filter id="eqGlow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d={`${path} L 900,420 L 60,420 Z`} fill="url(#eqGrad)" />
        <path d={path} fill="none" stroke="rgba(16,185,129,0.85)" strokeWidth="2.5" filter="url(#eqGlow)" />
        <path d={path} fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="1.2" />
      </svg>
    </div>
  )
}

function LogoColoredGrainFlow() {
  const rand = (i, offset = 0) => {
    const x = Math.sin(i * 12.9898 + offset * 78.233) * 43758.5453
    return x - Math.floor(x)
  }

  // Three color bands: YouTube (red), Reddit (orange), X (white)
  const bands = [
    { id: "yt", color: "rgba(239,68,68,0.85)", yOff: 18 },
    { id: "reddit", color: "rgba(249,115,22,0.80)", yOff: 0 },
    { id: "x", color: "rgba(255,255,255,0.70)", yOff: -18 },
  ]

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-25">
      <svg className="absolute inset-0 h-full w-full">
        <defs>
          <filter id="grainFilter">
            <feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="3" />
            <feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.2 0" />
          </filter>
        </defs>

        {bands.map(({ id, color, yOff }) => (
          <g key={id}>
            {Array.from({ length: 720 }).map((_, i) => {
              const t = i / 720
              const x = 120 + t * 790
              const wiggle = rand(i, 7) * 12 - 6
              const y = 298 + yOff + wiggle

              return (
                <circle
                  key={i}
                  cx={x}
                  cy={y}
                  r={rand(i, 3) * 1.4 + 0.8}
                  fill={color}
                  filter="url(#grainFilter)"
                  opacity={0.6 + rand(i, 5) * 0.3}
                />
              )
            })}
          </g>
        ))}
      </svg>
    </div>
  )
}

function LogoStream() {
  const tokens = [
    {
      kind: "x",
      Icon: SiX,
      delay: 0,
      color: "text-white",
      glow: "drop-shadow(0 0 24px rgba(255,255,255,0.6))",
      bg: "bg-white/10",
      border: "border-white/30",
      trailColor: "rgba(255,255,255,0.4)"
    },
    {
      kind: "reddit",
      Icon: SiReddit,
      delay: 1.2,
      color: "text-orange-500",
      glow: "drop-shadow(0 0 24px rgba(249,115,22,0.7))",
      bg: "bg-orange-500/10",
      border: "border-orange-500/30",
      trailColor: "rgba(249,115,22,0.5)"
    },
    {
      kind: "youtube",
      Icon: SiYoutube,
      delay: 2.4,
      color: "text-red-500",
      glow: "drop-shadow(0 0 24px rgba(239,68,68,0.7))",
      bg: "bg-red-500/10",
      border: "border-red-500/30",
      trailColor: "rgba(239,68,68,0.5)"
    },
    {
      kind: "x",
      Icon: SiX,
      delay: 3.6,
      color: "text-white",
      glow: "drop-shadow(0 0 24px rgba(255,255,255,0.6))",
      bg: "bg-white/10",
      border: "border-white/30",
      trailColor: "rgba(255,255,255,0.4)"
    },
    {
      kind: "reddit",
      Icon: SiReddit,
      delay: 4.8,
      color: "text-orange-500",
      glow: "drop-shadow(0 0 24px rgba(249,115,22,0.7))",
      bg: "bg-orange-500/10",
      border: "border-orange-500/30",
      trailColor: "rgba(249,115,22,0.5)"
    },
  ]

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <svg className="absolute inset-0 h-full w-full" style={{ zIndex: 25 }}>
        <defs>
          {tokens.map((token, i) => (
            <linearGradient key={`grad-${i}`} id={`trailGrad-${i}`} x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={token.trailColor} stopOpacity="0" />
              <stop offset="40%" stopColor={token.trailColor} stopOpacity="0.7" />
              <stop offset="100%" stopColor={token.trailColor} stopOpacity="0" />
            </linearGradient>
          ))}
        </defs>

        {tokens.map((token, i) => (
          <g key={`trail-group-${i}`}>
            <path
              className="logoRide"
              d="M120 298 C 230 250, 330 340, 450 304 C 550 274, 620 332, 720 296 C 800 270, 850 280, 910 258"
              stroke={`url(#trailGrad-${i})`}
              strokeWidth="28"
              fill="none"
              opacity="0.6"
              strokeLinecap="round"
              style={{
                animationDelay: `${token.delay}s`,
                filter: `blur(8px) drop-shadow(0 0 12px ${token.trailColor})`,
              }}
            />
          </g>
        ))}
      </svg>

      {tokens.map((token, i) => {
        const Icon = token.Icon
        return (
          <div
            key={i}
            className={`logoRide absolute flex h-16 w-16 items-center justify-center rounded-2xl border ${token.border} ${token.bg} backdrop-blur-md shadow-2xl`}
            style={{
              animationDelay: `${token.delay}s`,
              filter: token.glow,
              zIndex: 30,
            }}
          >
            <Icon className={`h-9 w-9 ${token.color}`} />
          </div>
        )
      })}
    </div>
  )
}

function AngledLaptop({ children }) {
  return (
    <div className="relative" style={{ width: '480px', height: '300px' }}>
      {/* Very subtle shadow */}
      <div className="absolute -inset-4 rounded-[32px] bg-black/30 blur-3xl opacity-50" style={{ transform: 'translateY(20px) scale(0.92)' }} />

      {/* Laptop screen - glass-like with minimal border */}
      <div
        className="absolute inset-0 rounded-[24px] overflow-hidden backdrop-blur-sm"
        style={{
          background: 'linear-gradient(145deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        {/* Subtle edge highlight */}
        <div className="absolute inset-0 rounded-[24px] opacity-20" style={{
          background: 'linear-gradient(125deg, rgba(255,255,255,0.05) 0%, transparent 30%, transparent 70%, rgba(0,0,0,0.1) 100%)',
        }} />

        {/* Screen content area - minimal dark background */}
        <div className="absolute inset-[6px] overflow-hidden rounded-[18px]" style={{
          background: 'rgba(0,0,0,0.4)',
        }}>
          {/* Very subtle glass reflection */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-transparent opacity-50 pointer-events-none" />
          <div className="absolute top-[10%] right-[15%] w-[35%] h-[25%] bg-white/[0.015] blur-2xl rounded-full pointer-events-none" />

          {children}
        </div>
      </div>

      {/* Bottom keyboard base - very subtle */}
      <div
        className="absolute left-[-6%] top-[100%] h-2.5 w-[112%] opacity-25"
        style={{
          background: 'linear-gradient(to bottom, rgba(255,255,255,0.03), rgba(255,255,255,0.01))',
          borderRadius: '0 0 20px 20px',
          transformOrigin: 'top center',
          border: '1px solid rgba(255,255,255,0.03)',
          borderTop: 'none',
        }}
      />
    </div>
  )
}

function ComputerRealisticTradingScreen() {
  const rand = (i, offset = 0) => {
    const x = Math.sin(i * 12.9898 + offset * 78.233) * 43758.5453
    return x - Math.floor(x)
  }

  // Generate realistic OHLC candle data
  const candles = useMemo(() => {
    const bars = []
    let close = 150
    for (let i = 0; i < 24; i++) {
      const open = close
      const change = (rand(i, 1) - 0.5) * 8
      const hi = Math.max(open, open + change) + rand(i, 2) * 3
      const lo = Math.min(open, open + change) - rand(i, 3) * 3
      close = open + change
      bars.push({ open, high: hi, low: lo, close })
    }
    return bars
  }, [])

  // Moving average
  const maPoints = useMemo(() => {
    const pts = []
    for (let i = 0; i < candles.length; i++) {
      const start = Math.max(0, i - 4)
      const slice = candles.slice(start, i + 1)
      const avg = slice.reduce((sum, c) => sum + c.close, 0) / slice.length
      pts.push(avg)
    }
    return pts
  }, [candles])

  return (
    <div className="relative h-full w-full overflow-hidden p-3" style={{
      background: 'linear-gradient(to bottom right, rgba(0,0,0,0.5), rgba(0,0,0,0.3))'
    }}>
      {/* Header */}
      <div className="mb-2 flex items-center justify-between border-b border-white/20 pb-2 text-[10px]">
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-mono text-white/80 font-medium">LIVE</span>
        </div>
        <span className="font-mono text-emerald-300 font-semibold tracking-wide">AAPL</span>
        <span className="text-white/60 font-medium">1H</span>
      </div>

      {/* Price info */}
      <div className="mb-3 flex items-baseline gap-3 text-[11px]">
        <span className="font-mono text-white font-semibold">$172.45</span>
        <span className="text-emerald-300 font-medium">+2.3%</span>
      </div>

      {/* Trading Chart */}
      <div className="relative h-[calc(100%-32px)]">
        <svg viewBox="0 0 240 140" className="h-full w-full" preserveAspectRatio="none">
          <defs>
            <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(16,185,129,0.15)" />
              <stop offset="100%" stopColor="rgba(16,185,129,0)" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 35, 70, 105, 140].map((y) => (
            <line key={y} x1="0" y1={y} x2="240" y2={y} stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
          ))}

          {/* Candles */}
          {candles.map((bar, i) => {
            const x = 8 + i * 9.5
            const scale = 140 / 30
            const yOpen = 140 - (bar.open - 140) * scale
            const yClose = 140 - (bar.close - 140) * scale
            const yHigh = 140 - (bar.high - 140) * scale
            const yLow = 140 - (bar.low - 140) * scale

            const isGreen = bar.close >= bar.open
            const color = isGreen ? "rgba(16,185,129,0.95)" : "rgba(239,68,68,0.95)"
            const bodyTop = Math.min(yOpen, yClose)
            const bodyHeight = Math.abs(yClose - yOpen) || 0.8

            return (
              <g key={i}>
                {/* Wick */}
                <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={color} strokeWidth="1" opacity="0.75" />
                {/* Body */}
                <rect x={x - 2.5} y={bodyTop} width="5" height={bodyHeight} fill={color} rx="1" />
              </g>
            )
          })}

          {/* Moving Average */}
          <path
            d={`M ${maPoints.map((avg, i) => {
              const x = 8 + i * 9.5
              const y = 140 - (avg - 140) * (140 / 30)
              return `${i === 0 ? '' : 'L '}${x},${y}`
            }).join(' ')}`}
            fill="none"
            stroke="rgba(139,92,246,0.85)"
            strokeWidth="1.5"
            filter="drop-shadow(0 0 3px rgba(139,92,246,0.4))"
          />
        </svg>

        {/* Volume bars */}
        <div className="absolute bottom-0 left-0 right-0 flex items-end gap-[5.5px] px-2 h-4 opacity-30">
          {candles.map((_, i) => (
            <div
              key={i}
              className="flex-1 bg-white/40 rounded-t"
              style={{ height: `${30 + rand(i, 7) * 70}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
