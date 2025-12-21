import { useState, lazy, Suspense, useMemo } from 'react'
import { SiX, SiReddit, SiYoutube } from 'react-icons/si'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import Login from './Login'
import Signup from './Signup'
import StrategyCarousel from './StrategyCarousel'
import { ManualWorkflowMockChaos } from './ManualWorkflowMockChaos'

const ObservabilityGraph = lazy(() => import('./ObservabilityGraph'))

export default function LandingPage({ onGetStarted, onShowSignup, user, onSignOut, onShowBotLibrary }) {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
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
    if (email) {
      // Store email in localStorage or handle it as needed
      localStorage.setItem('userEmail', email)
    }
    // Show signup/login or navigate to dashboard
    if (isAuthenticated) {
      onGetStarted?.()
    } else {
      setShowSignup(true)
    }
  }

  return (
    <div className="w-full bg-black">
      {/* Navbar - always visible */}
      <div className="sticky top-0 z-50 bg-dark-surface/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="text-white hover:opacity-80 transition-opacity"
          >
            <span className="text-2xl font-serif italic">Mobius</span>
          </button>

        <div className="flex items-center gap-3">
          {/* Dashboard & Community buttons - always visible */}
          <button
            onClick={onGetStarted}
            className="px-4 py-2 text-sm font-light rounded-lg border border-white/20 text-white/80 hover:border-accent hover:text-accent transition-colors"
          >
            Dashboard
          </button>
          <button
            onClick={() => navigate('/community')}
            className="px-4 py-2 text-sm font-light rounded-lg border border-white/20 text-white/80 hover:border-accent hover:text-accent transition-colors"
          >
            Community
          </button>

          {isAuthenticated ? (
            // Authenticated user - show name and settings
            <div className="flex items-center gap-2 pl-3 border-l border-gray-700">
              <span className="text-sm text-gray-400">
                {user?.full_name ? user.full_name.split(' ')[0] : user?.email}
              </span>
              <div className="relative group">
                <button className="text-sm text-gray-400 hover:text-white p-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                <div className="absolute right-0 top-full mt-1 w-32 bg-dark-surface rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-1">
                    <button
                      onClick={onShowBotLibrary}
                      className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-dark-bg hover:text-white transition-colors"
                    >
                      My Bots
                    </button>
                    <button
                      onClick={onSignOut}
                      className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-dark-bg hover:text-red-300 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Unauthenticated user - show sign in and sign up buttons
            <>
              <button
                onClick={() => setShowLogin(true)}
                className="btn btn-secondary text-sm"
              >
                Sign In
              </button>
              <button
                onClick={onShowSignup}
                className="px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-100 transition-colors"
              >
                Sign Up
              </button>
            </>
          )}
        </div>
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
                onKeyPress={(e) => e.key === 'Enter' && handleGetStarted()}
                placeholder="Your Email Address"
                className="flex-1 px-8 py-6 bg-transparent text-white placeholder-gray-400 outline-none text-xl"
              />
              <button
                onClick={handleGetStarted}
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
          <div className="w-1/2 h-full absolute right-[-20rem] top-14 flex items-center justify-center pointer-events-none overflow-hidden" style={{ isolation: 'isolate' }}>
            <div className="w-full h-full flex items-center justify-center overflow-hidden">
              <iframe
                src='https://my.spline.design/mobiusmiamisunsetcopy-SKOxlmvEV8x6vDuzNWCJ8AFf/'
                width='100%'
                height='100%'
                title="Mobius 3D Logo"
                style={{ border: 'none', pointerEvents: 'auto', background: 'transparent' }}
              />
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
              Without Mobius, <span className="italic font-light text-violet-400">it's chaos.</span>
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
                With Mobius, it's <span className="italic text-violet-400">effortless.</span>
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

            {/* Right: Phone Mockup */}
            <div className="relative lg:pl-8">
              {/* iPhone-style mockup */}
              <div className="relative mx-auto w-[340px]">
                {/* Phone frame */}
                <div className="relative rounded-[3rem] border-[12px] border-gray-800 bg-black shadow-2xl">
                  {/* Notch */}
                  <div className="absolute left-1/2 top-0 z-10 h-7 w-40 -translate-x-1/2 rounded-b-2xl bg-gray-800" />

                  {/* Screen content */}
                  <div className="relative overflow-hidden rounded-[2rem] bg-gradient-to-b from-gray-900 to-black">
                    {/* Status bar */}
                    <div className="flex items-center justify-between px-8 pt-3 pb-2">
                      <span className="text-xs text-white/90 font-medium">9:41</span>
                      <div className="flex items-center gap-1">
                        <svg className="h-3 w-3 text-white/90" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                        </svg>
                        <svg className="h-3 w-3 text-white/90" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M17.778 8.222c-4.296-4.296-11.26-4.296-15.556 0A1 1 0 01.808 6.808c5.076-5.077 13.308-5.077 18.384 0a1 1 0 01-1.414 1.414zM14.95 11.05a7 7 0 00-9.9 0 1 1 0 01-1.414-1.414 9 9 0 0112.728 0 1 1 0 01-1.414 1.414zM12.12 13.88a3 3 0 00-4.242 0 1 1 0 01-1.415-1.415 5 5 0 017.072 0 1 1 0 01-1.415 1.415zM9 16a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clipRule="evenodd" />
                        </svg>
                        <svg className="h-4 w-6 text-white/90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <rect x="1" y="6" width="18" height="12" rx="2" strokeWidth="2" />
                          <path d="M19 10h2a1 1 0 011 1v2a1 1 0 01-1 1h-2" strokeWidth="2" />
                        </svg>
                      </div>
                    </div>

                    {/* Portfolio value */}
                    <div className="px-6 pt-6 pb-4">
                      <p className="text-xs text-white/50 font-medium">Total Portfolio Value</p>
                      <h3 className="mt-1 text-4xl font-light text-white">$1,620.44</h3>
                      <p className="mt-1 text-sm text-emerald-400 font-medium">+$124.32 (8.3%)</p>
                    </div>

                    {/* Main Chart */}
                    <div className="px-6 pb-6">
                      <svg className="w-full h-32" viewBox="0 0 300 120" fill="none">
                        <defs>
                          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="rgb(16, 185, 129)" stopOpacity="0.3" />
                            <stop offset="100%" stopColor="rgb(16, 185, 129)" stopOpacity="0" />
                          </linearGradient>
                        </defs>
                        <path
                          d="M0,80 L30,75 L60,70 L90,65 L120,68 L150,55 L180,50 L210,45 L240,42 L270,35 L300,30"
                          stroke="rgb(16, 185, 129)"
                          strokeWidth="2.5"
                          fill="none"
                        />
                        <path
                          d="M0,80 L30,75 L60,70 L90,65 L120,68 L150,55 L180,50 L210,45 L240,42 L270,35 L300,30 L300,120 L0,120 Z"
                          fill="url(#chartGradient)"
                        />
                      </svg>
                    </div>

                    {/* AI Agents Section */}
                    <div className="px-6 pb-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-medium text-white/90">AI Agents</h4>
                        <span className="text-xs text-emerald-400 font-medium">3 Active</span>
                      </div>
                      <div className="flex gap-2">
                        <div className="flex-1 rounded-xl bg-violet-500/20 border border-violet-500/30 px-3 py-2">
                          <p className="text-xs text-violet-300 font-medium">Momentum</p>
                        </div>
                        <div className="flex-1 rounded-xl bg-emerald-500/20 border border-emerald-500/30 px-3 py-2">
                          <p className="text-xs text-emerald-300 font-medium">Value</p>
                        </div>
                        <div className="flex-1 rounded-xl bg-blue-500/20 border border-blue-500/30 px-3 py-2">
                          <p className="text-xs text-blue-300 font-medium">Growth</p>
                        </div>
                      </div>
                    </div>

                    {/* Holdings */}
                    <div className="px-6 pb-8">
                      <h4 className="text-sm font-medium text-white/90 mb-3">Holdings</h4>
                      <div className="space-y-2">
                        <HoldingRow symbol="AAPL" shares="12" value="$2,124" change="+4.2%" positive />
                        <HoldingRow symbol="TSLA" shares="8" value="$1,896" change="+12.8%" positive />
                        <HoldingRow symbol="NVDA" shares="15" value="$6,420" change="+18.4%" positive />
                        <HoldingRow symbol="GOOGL" shares="20" value="$2,680" change="-2.1%" positive={false} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Glow effect */}
                <div className="absolute inset-0 -z-10 rounded-[3rem] bg-gradient-to-br from-violet-500/30 to-emerald-500/20 blur-3xl" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black border-t border-white/5 py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12">
            <div className="md:col-span-1">
              <h3 className="text-2xl font-serif italic text-white mb-4">Mobius</h3>
              <p className="text-sm text-white/50">
                AI-powered trading from strategy to deployment
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white/90 mb-4">Product</h4>
              <ul className="space-y-3">
                <li><button onClick={() => scrollToSection('process')} className="text-sm text-white/50 hover:text-white/90 transition-colors">How it Works</button></li>
                <li><button onClick={handleBuildBot} className="text-sm text-white/50 hover:text-white/90 transition-colors">Build Bot</button></li>
                <li><button onClick={() => navigate('/community')} className="text-sm text-white/50 hover:text-white/90 transition-colors">Community</button></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white/90 mb-4">Company</h4>
              <ul className="space-y-3">
                <li><a href="#" className="text-sm text-white/50 hover:text-white/90 transition-colors">About</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white/90 transition-colors">Blog</a></li>
                <li><a href="#" className="text-sm text-white/50 hover:text-white/90 transition-colors">Careers</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-medium text-white/90 mb-4">Connect</h4>
              <div className="flex gap-4">
                <a href="https://x.com" target="_blank" rel="noopener noreferrer" className="text-white/50 hover:text-white/90 transition-colors">
                  <SiX className="w-5 h-5" />
                </a>
                <a href="https://reddit.com" target="_blank" rel="noopener noreferrer" className="text-white/50 hover:text-white/90 transition-colors">
                  <SiReddit className="w-5 h-5" />
                </a>
                <a href="https://youtube.com" target="_blank" rel="noopener noreferrer" className="text-white/50 hover:text-white/90 transition-colors">
                  <SiYoutube className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-white/5">
            <p className="text-center text-sm text-white/40">
              © 2024 Mobius. All rights reserved.
            </p>
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

// Holding Row Component
function HoldingRow({ symbol, shares, value, change, positive }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-white/5">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500/20 to-violet-600/10 flex items-center justify-center">
          <span className="text-xs font-bold text-violet-300">{symbol[0]}</span>
        </div>
        <div>
          <p className="text-sm font-medium text-white/90">{symbol}</p>
          <p className="text-xs text-white/40">{shares} shares</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-white/90">{value}</p>
        <p className={`text-xs font-medium ${positive ? 'text-emerald-400' : 'text-red-400'}`}>
          {change}
        </p>
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
    const pts = []
    let y = 280
    for (let i = 0; i <= 60; i++) {
      const x = 80 + i * 13
      y += (Math.random() - 0.42) * 16
      y = Math.max(120, Math.min(360, y))
      pts.push(`${x},${y}`)
    }
    return `M ${pts.join(' L ')}`
  }, [])

  return (
    <div className="absolute inset-0 flex items-center justify-center opacity-25">
      <svg
        viewBox="0 0 900 420"
        className="h-full w-auto"
        style={{ filter: 'blur(0.6px)' }}
      >
        <defs>
          <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgb(168,85,247)" stopOpacity="0.12" />
            <stop offset="100%" stopColor="rgb(168,85,247)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={`${path} L 900,420 L 80,420 Z`} fill="url(#eqGrad)" />
        <path d={path} fill="none" stroke="rgba(168,85,247,0.4)" strokeWidth="1.8" />
      </svg>
    </div>
  )
}

function LogoColoredGrainFlow() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-30">
      <svg className="absolute inset-0 h-full w-full">
        <defs>
          <radialGradient id="meshGrad1">
            <stop offset="0%" stopColor="rgb(168,85,247)" stopOpacity="0.25" />
            <stop offset="100%" stopColor="rgb(16,185,129)" stopOpacity="0.08" />
          </radialGradient>
          <filter id="noiseFilter">
            <feTurbulence type="fractalNoise" baseFrequency="1.8" numOctaves="2" />
            <feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.15 0" />
          </filter>
        </defs>
        <path
          d="M120 298 C 230 250, 330 340, 450 304 C 550 274, 620 332, 720 296 C 800 270, 850 280, 910 258"
          stroke="url(#meshGrad1)"
          strokeWidth="80"
          fill="none"
          opacity="0.5"
          filter="url(#noiseFilter)"
        />
      </svg>
    </div>
  )
}

function LogoStream() {
  const logos = ['A', 'T', 'N', 'G', 'M']
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {logos.map((letter, i) => (
        <div
          key={i}
          className="logoRide absolute flex h-7 w-7 items-center justify-center rounded-md border border-white/20 bg-white/5 text-xs font-bold text-white/70 backdrop-blur-sm"
          style={{
            animationDelay: `${i * 1.2}s`,
          }}
        >
          {letter}
        </div>
      ))}
    </div>
  )
}

function AngledLaptop({ children }) {
  return (
    <div className="relative" style={{ width: '280px', height: '180px' }}>
      {/* Laptop bezel */}
      <div className="absolute inset-0 rounded-lg border-4 border-gray-700 bg-gray-900 shadow-2xl overflow-hidden">
        {/* Screen */}
        <div className="absolute inset-1 overflow-hidden rounded-sm bg-black">
          {children}
        </div>
      </div>
      {/* Keyboard base */}
      <div
        className="absolute left-[-10%] top-[100%] h-3 w-[120%] rounded-b-lg bg-gray-800"
        style={{ transformOrigin: 'top center' }}
      />
    </div>
  )
}

function ComputerRealisticTradingScreen() {
  return (
    <div className="relative h-full w-full overflow-hidden bg-gradient-to-br from-gray-950 to-black p-2 text-[6px]">
      {/* Tiny terminal header */}
      <div className="mb-1 flex items-center gap-1 border-b border-white/10 pb-1">
        <div className="h-1 w-1 rounded-full bg-red-400/70" />
        <div className="h-1 w-1 rounded-full bg-yellow-400/60" />
        <div className="h-1 w-1 rounded-full bg-emerald-400/60" />
        <span className="ml-1 text-white/50">trading_bot.py</span>
      </div>

      {/* Tiny code snippet */}
      <div className="space-y-0.5 font-mono">
        <div className="text-violet-400">
          <span className="text-white/60">{'>'}</span> python run_strategy.py
        </div>
        <div className="text-emerald-400">
          [INFO] Strategy loaded: RSI_Momentum
        </div>
        <div className="text-white/60">
          [INFO] Backtesting 2020-2024...
        </div>
        <div className="text-emerald-400">
          [SUCCESS] Total return: +64.2%
        </div>
        <div className="flex items-center gap-1">
          <div className="h-1 w-1 animate-pulse rounded-full bg-emerald-400" />
          <span className="text-white/70">Deploying to Alpaca...</span>
        </div>
      </div>

      {/* Tiny mini-chart */}
      <div className="mt-2">
        <svg className="h-8 w-full opacity-40" viewBox="0 0 100 30">
          <path
            d="M0,20 L20,18 L40,14 L60,16 L80,10 L100,8"
            stroke="rgb(16,185,129)"
            strokeWidth="0.8"
            fill="none"
          />
        </svg>
      </div>
    </div>
  )
}
