import { useState } from 'react'

export default function GetStartedPage() {
  const [email, setEmail] = useState('')

  const handleGetStarted = () => {
    if (email) {
      localStorage.setItem('userEmail', email)
      // TODO: Handle what happens after email is entered
      console.log('Email saved:', email)
    }
  }

  return (
    <div className="w-full bg-black min-h-screen">
      {/* Navbar - Just Logo */}
      <div className="sticky top-0 z-50 bg-dark-surface/50 backdrop-blur-sm">
        <div className="w-full px-6 py-6">
          <button
            onClick={() => window.location.href = '/'}
            className="flex items-center gap-4 text-white hover:opacity-80 transition-opacity"
          >
            <img
              src="/logo.png"
              alt="Mobius Logo"
              className="h-16 w-16 brightness-125"
            />
            <span className="text-3xl font-light">Mobius</span>
          </button>
        </div>
      </div>

      {/* Hero Section */}
      <section className="w-full h-screen overflow-hidden relative bg-black">
        {/* Aurora gradient backdrop */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          <div className="absolute -left-40 top-24 h-[520px] w-[520px] rounded-full bg-[radial-gradient(circle_at_center,rgba(168,85,247,0.55),transparent_60%)] blur-3xl opacity-70" />
          <div className="absolute left-1/2 top-0 h-[700px] w-[700px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.35),transparent_65%)] blur-3xl opacity-60" />
          <div className="absolute right-[-220px] top-[-120px] h-[720px] w-[720px] rounded-full bg-[conic-gradient(from_180deg,rgba(168,85,247,0.0),rgba(168,85,247,0.55),rgba(168,85,247,0.0))] blur-3xl opacity-60" />
        </div>

        <div className="max-w-7xl mx-auto h-full px-6 flex items-center">
          {/* Left side - Content */}
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

            {/* Integration logos */}
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
    </div>
  )
}
