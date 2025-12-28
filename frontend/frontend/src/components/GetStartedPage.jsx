import { useState, useEffect } from 'react'
import ObservabilityGraph from './ObservabilityGraph'

// SVG Component for Discovery Call Mock (unused, kept for reference)
function MobiusDiscoveryMock({ className = "" }) {
  return (
    <svg
      className={className}
      viewBox="0 0 640 480"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Discovery call mock UI illustration"
    >
      <defs>
        <radialGradient id="bgGlow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(480 40) rotate(130) scale(520 520)">
          <stop stopColor="#A855F7" stopOpacity="0.35" />
          <stop offset="1" stopColor="#0B0B14" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="card" x1="0" y1="0" x2="0" y2="480" gradientUnits="userSpaceOnUse">
          <stop stopColor="#121225" stopOpacity="0.92" />
          <stop offset="1" stopColor="#0A0A14" stopOpacity="0.92" />
        </linearGradient>
        <linearGradient id="stroke" x1="0" y1="0" x2="640" y2="480" gradientUnits="userSpaceOnUse">
          <stop stopColor="#A855F7" stopOpacity="0.65" />
          <stop offset="1" stopColor="#60A5FA" stopOpacity="0.25" />
        </linearGradient>
        <filter id="glassBlur" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="10" />
        </filter>
        <filter id="outerGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="14" result="blur" />
          <feColorMatrix
            in="blur"
            type="matrix"
            values="
              1 0 0 0 0.45
              0 1 0 0 0.20
              0 0 1 0 0.85
              0 0 0 0.35 0"
            result="glow"
          />
          <feMerge>
            <feMergeNode in="glow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="innerShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feOffset dx="0" dy="8" />
          <feGaussianBlur stdDeviation="10" result="shadow" />
          <feComposite in="shadow" in2="SourceAlpha" operator="out" result="shadowCut" />
          <feColorMatrix
            in="shadowCut"
            type="matrix"
            values="
              0 0 0 0 0
              0 0 0 0 0
              0 0 0 0 0
              0 0 0 0.55 0"
          />
          <feMerge>
            <feMergeNode />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient id="lineGrad" x1="140" y1="360" x2="520" y2="360" gradientUnits="userSpaceOnUse">
          <stop stopColor="#A855F7" stopOpacity="0.95" />
          <stop offset="1" stopColor="#60A5FA" stopOpacity="0.75" />
        </linearGradient>
        <linearGradient id="pillGrad" x1="0" y1="0" x2="120" y2="0" gradientUnits="userSpaceOnUse">
          <stop stopColor="#A855F7" stopOpacity="0.35" />
          <stop offset="1" stopColor="#A855F7" stopOpacity="0.15" />
        </linearGradient>
      </defs>
      <rect width="640" height="480" rx="28" fill="url(#bgGlow)" />
      <rect x="0" y="0" width="640" height="480" rx="28" fill="#070712" />
      <g filter="url(#outerGlow)">
        <rect x="70" y="60" width="500" height="360" rx="22" fill="url(#card)" />
        <rect x="70.75" y="60.75" width="498.5" height="358.5" rx="21.25" stroke="url(#stroke)" strokeOpacity="0.35" />
      </g>
      <g opacity="0.95">
        <rect x="105" y="92" width="108" height="34" rx="12" fill="url(#pillGrad)" stroke="#A855F7" strokeOpacity="0.35" />
        <text x="159" y="114" textAnchor="middle" fontSize="12" fill="#EDE9FE" fontFamily="ui-sans-serif, system-ui">
          All Tasks
        </text>
        <text x="250" y="114" fontSize="12" fill="#B9B2D6" fontFamily="ui-sans-serif, system-ui" opacity="0.8">
          Waiting for approval
        </text>
        <line x1="105" y1="146" x2="535" y2="146" stroke="#FFFFFF" strokeOpacity="0.06" />
      </g>
      {[
        { y: 170, title: "Share your trading journey", sub: "Goals • style • time horizon", status: "pending" },
        { y: 238, title: "Live demo walkthrough", sub: "Backtest → paper bot → live", status: "done" },
        { y: 306, title: "Q&A + next steps", sub: "Answer questions • collect feedback", status: "x" },
      ].map((t, i) => (
        <g key={i} filter="url(#innerShadow)">
          <rect x="105" y={t.y} width="430" height="56" rx="16" fill="#0B0B16" opacity="0.9" stroke="#FFFFFF" strokeOpacity="0.06" />
          <circle cx="132" cy={t.y + 28} r="12" fill="#A855F7" fillOpacity="0.18" stroke="#A855F7" strokeOpacity="0.35" />
          <path
            d="M126.5 196.5h11M126.5 200.5h7"
            transform={`translate(0 ${t.y - 170})`}
            stroke="#EDE9FE"
            strokeOpacity="0.85"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <text x="155" y={t.y + 24} fontSize="14" fill="#F5F3FF" fontFamily="ui-sans-serif, system-ui">
            {t.title}
          </text>
          <text x="155" y={t.y + 42} fontSize="11" fill="#B9B2D6" fontFamily="ui-sans-serif, system-ui" opacity="0.85">
            {t.sub}
          </text>
          {t.status === "pending" && (
            <circle cx="517" cy={t.y + 28} r="8" fill="none" stroke="#A855F7" strokeOpacity="0.7" strokeWidth="2" />
          )}
          {t.status === "done" && (
            <g>
              <circle cx="517" cy={t.y + 28} r="8" fill="#22C55E" fillOpacity="0.12" stroke="#22C55E" strokeOpacity="0.7" />
              <path d={`M513 ${t.y + 28} l2 2 l6-7`} stroke="#86EFAC" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </g>
          )}
          {t.status === "x" && (
            <g opacity="0.6">
              <circle cx="517" cy={t.y + 28} r="8" fill="#EF4444" fillOpacity="0.08" stroke="#EF4444" strokeOpacity="0.4" />
              <path d={`M513 ${t.y + 24} L521 ${t.y + 32}`} stroke="#FCA5A5" strokeWidth="2" strokeLinecap="round" />
              <path d={`M521 ${t.y + 24} L513 ${t.y + 32}`} stroke="#FCA5A5" strokeWidth="2" strokeLinecap="round" />
            </g>
          )}
        </g>
      ))}
      <g opacity="0.95">
        <text x="105" y="392" fontSize="12" fill="#B9B2D6" fontFamily="ui-sans-serif, system-ui">
          Example equity curve
        </text>
        <rect x="105" y="404" width="430" height="6" rx="3" fill="#FFFFFF" fillOpacity="0.06" />
        <rect x="105" y="404" width="230" height="6" rx="3" fill="url(#lineGrad)" opacity="0.65" />
        <path
          d="M120 368 C 165 350, 190 392, 230 366 C 270 340, 305 388, 345 360 C 385 332, 420 378, 455 346 C 480 322, 505 336, 520 330"
          stroke="url(#lineGrad)"
          strokeWidth="3"
          strokeLinecap="round"
          fill="none"
          opacity="0.9"
        />
        <path
          d="M120 368 C 165 350, 190 392, 230 366 C 270 340, 305 388, 345 360 C 385 332, 420 378, 455 346 C 480 322, 505 336, 520 330 L520 402 L120 402 Z"
          fill="url(#lineGrad)"
          opacity="0.10"
        />
      </g>
      <circle cx="96" cy="78" r="2" fill="#A855F7" opacity="0.55" />
      <circle cx="560" cy="110" r="1.7" fill="#60A5FA" opacity="0.45" />
      <circle cx="540" cy="420" r="2" fill="#A855F7" opacity="0.35" />
    </svg>
  )
}

// Discovery Call Info Sections
const INFO_SECTIONS = [
  {
    id: 1,
    category: 'Workflow Automation',
    title: 'Automate repetitive tasks',
    description: 'We help you streamline internal operations by automating manual workflows like data entry, reporting, and approval chains saving time and cutting down errors.',
    tags: ['Internal Task Bots', '100+ Automations']
  },
  {
    id: 2,
    category: 'Platform Demo',
    title: 'See Mobius in Action',
    description: 'Get a personalized walkthrough of the Mobius platform. We\'ll show you how our AI agents analyze social sentiment, execute trades, and help you stay ahead of market trends.',
    tags: ['Live Demo', 'AI Agents', 'Features']
  },
  {
    id: 3,
    category: 'Q&A Session',
    title: 'Get Your Questions Answered',
    description: 'This is your time to ask anything about Mobius, our technology, pricing, or how we can help solve your specific trading challenges. We\'re here to help you make an informed decision.',
    tags: ['Questions', 'Pricing', 'Next Steps']
  }
]

export default function GetStartedPage() {
  const [email, setEmail] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)


  const handleJoinWaitlist = async () => {
    if (!email) return

    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/email/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      if (response.ok) {
        console.log('✅ Email subscribed successfully')
        localStorage.setItem('userEmail', email)
        setIsSubmitted(true)
      }
    } catch (error) {
      console.error('Error subscribing email:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 w-full h-full overflow-auto">
      {/* Purple Gradient Background - Mobius Theme - Fixed to cover entire viewport */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Base gradient matching Mobius purple theme */}
        <div
          className="w-full h-full"
          style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(168,85,247,0.3) 0%, rgba(139,92,246,0.2) 30%, rgba(109,40,217,0.1) 60%, rgba(0,0,0,1) 100%)',
          }}
        />

        {/* Animated floating elements */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Stars/particles */}
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-white"
              style={{
                width: Math.random() * 3 + 1 + 'px',
                height: Math.random() * 3 + 1 + 'px',
                top: Math.random() * 100 + '%',
                left: Math.random() * 100 + '%',
                opacity: Math.random() * 0.5 + 0.1,
                animation: `twinkle ${Math.random() * 3 + 2}s ease-in-out infinite`,
                animationDelay: `${Math.random() * 2}s`,
              }}
            />
          ))}

          {/* Larger glowing orbs */}
          <div
            className="absolute w-64 h-64 rounded-full blur-3xl opacity-20"
            style={{
              background: 'radial-gradient(circle, rgba(168,85,247,0.8) 0%, transparent 70%)',
              top: '20%',
              left: '10%',
              animation: 'float 8s ease-in-out infinite',
            }}
          />
          <div
            className="absolute w-48 h-48 rounded-full blur-3xl opacity-15"
            style={{
              background: 'radial-gradient(circle, rgba(139,92,246,0.8) 0%, transparent 70%)',
              top: '60%',
              right: '15%',
              animation: 'float 10s ease-in-out infinite reverse',
              animationDelay: '2s',
            }}
          />
          <div
            className="absolute w-56 h-56 rounded-full blur-3xl opacity-10"
            style={{
              background: 'radial-gradient(circle, rgba(109,40,217,0.8) 0%, transparent 70%)',
              bottom: '10%',
              left: '50%',
              animation: 'float 12s ease-in-out infinite',
              animationDelay: '4s',
            }}
          />
        </div>

        {/* Grain overlay */}
        <div
          className="absolute inset-0 opacity-[0.05] mix-blend-overlay"
          style={{ backgroundImage: `url('https://grainy-gradients.vercel.app/noise.svg')` }}
        />
      </div>

      {/* Add keyframe animations */}
      <style>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0.1; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.2); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          33% { transform: translateY(-30px) translateX(20px); }
          66% { transform: translateY(20px) translateX(-20px); }
        }
      `}</style>

      {/* Navbar */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/5">
        <div className="w-full px-6 py-6">
          <button
            onClick={() => window.location.href = '/'}
            className="flex items-center gap-4 text-white hover:opacity-80 transition-opacity"
          >
            <img
              src="/logo.png"
              alt="Mobius Logo"
              className="h-12 w-12 brightness-125"
            />
            <span className="text-2xl font-light">Mobius</span>
          </button>
        </div>
      </div>

      {/* Main Waitlist Container */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-6 pt-24 pb-0">
        <div className="w-full max-w-3xl text-center">
          {/* Title */}
          <h1 className="text-6xl md:text-7xl font-normal text-white mb-6 leading-tight">
            Join the Waitlist
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-gray-400 mb-12">
            Be first to turn the timeline into trades
          </p>

          {/* Email Input Section */}
          {!isSubmitted ? (
            <div className="max-w-xl mx-auto mb-8">
              <div className="flex items-center gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleJoinWaitlist()}
                  placeholder="Your Email Address"
                  className="flex-1 px-6 py-4 bg-white/5 backdrop-blur-sm text-white placeholder-gray-500 border border-white/10 rounded-lg outline-none focus:border-purple-500/50 transition-colors text-base"
                />
                <button
                  onClick={handleJoinWaitlist}
                  disabled={!email || isLoading}
                  className="px-12 py-4 text-black font-semibold rounded-full hover:opacity-90 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all text-base whitespace-nowrap shadow-lg"
                  style={{ backgroundColor: '#ffffff' }}
                >
                  {isLoading ? 'Joining...' : 'Get Started'}
                </button>
              </div>
            </div>
          ) : (
            <div className="max-w-xl mx-auto mb-8">
              <div className="inline-flex items-center gap-3 px-6 py-4 bg-gradient-to-r from-emerald-500/20 to-green-500/20 border border-emerald-500/30 rounded-xl">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <p className="text-emerald-300 font-semibold text-lg">You're on the waitlist! We'll be in touch soon.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* First Section - Workflow Automation */}
      <div className="relative z-10 px-6 pt-0 pb-32">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Left Side - Performance Graph */}
            <div className="relative">
              <ObservabilityGraph
                title=""
                subtitle=""
                hideTooltip={true}
                hideLegend={true}
                hideAxes={true}
              />
            </div>

            {/* Right Side - Content */}
            <div>
              <div className="inline-block mb-6">
                <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-400 font-medium">
                  Understanding Your Needs
                </span>
              </div>

              <h2 className="text-4xl md:text-5xl font-normal text-white mb-6 leading-tight">
                Share Your Trading Journey
              </h2>

              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                We start by understanding your trading experience, goals, and challenges.
                Whether you're just getting started or looking to scale your trading, we'll discuss what you're hoping to achieve.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Second Section - AI Assistant */}
      <div className="relative z-10 px-6 pb-32">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Left Side - Content */}
            <div>
              <div className="inline-block mb-6">
                <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-400 font-medium">
                  Platform Demo
                </span>
              </div>

              <h2 className="text-4xl md:text-5xl font-normal text-white mb-6 leading-tight">
                See Mobius in Action
              </h2>

              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                Get a personalized walkthrough of the Mobius platform. We'll show you how our AI agents analyze social sentiment, execute trades, and help you stay ahead of market trends.
              </p>
            </div>

            {/* Right Side - Dashboard Mockup */}
            <div className="relative">
              <div className="bg-gradient-to-br from-gray-900/90 via-black/80 to-gray-900/90 backdrop-blur-xl rounded-3xl border border-white/10 p-6">
                {/* Dashboard Header */}
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
                  <h3 className="text-sm text-white font-medium">Trading Bot Dashboard</h3>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    <span className="text-xs text-green-400">Live</span>
                  </div>
                </div>

                {/* Performance Stats */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Total Return</div>
                    <div className="text-lg font-semibold text-green-400">+24.5%</div>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Win Rate</div>
                    <div className="text-lg font-semibold text-white">68%</div>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                    <div className="text-xs text-gray-400 mb-1">Total Trades</div>
                    <div className="text-lg font-semibold text-white">127</div>
                  </div>
                </div>

                {/* Mini Performance Chart */}
                <div className="bg-black/40 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-400">Performance</span>
                    <span className="text-xs text-green-400">+$2,450</span>
                  </div>
                  <svg viewBox="0 0 300 80" className="w-full h-16">
                    <defs>
                      <linearGradient id="performanceGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#8b5cf6" />
                        <stop offset="100%" stopColor="#a78bfa" />
                      </linearGradient>
                    </defs>
                    <path
                      d="M 0 60 Q 30 45, 60 50 T 120 35 T 180 30 T 240 20 T 300 15"
                      stroke="url(#performanceGrad)"
                      strokeWidth="2"
                      fill="none"
                    />
                  </svg>
                </div>

                {/* Recent Trade */}
                <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-400">Latest Trade</span>
                    <span className="px-2 py-0.5 bg-green-500/20 border border-green-500/30 rounded text-xs text-green-400">Profit</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-white font-medium">TSLA</div>
                      <div className="text-xs text-gray-400">Closed 2h ago</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-green-400 font-semibold">+$124.50</div>
                      <div className="text-xs text-gray-400">+3.2%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Third Section - Sales & Marketing */}
      <div className="relative z-10 px-6 pb-32">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Left Side - Contact Form */}
            <div className="relative">
              <div className="bg-gradient-to-br from-gray-900/90 via-black/80 to-gray-900/90 backdrop-blur-xl rounded-3xl border border-white/10 p-6">
                {/* Form Header */}
                <div className="mb-6 pb-3 border-b border-white/10">
                  <h3 className="text-sm text-white font-medium">Ask Us Anything</h3>
                  <p className="text-xs text-gray-400 mt-1">We'll get back to you within 24 hours</p>
                </div>

                {/* Contact Form Fields */}
                <div className="space-y-4">
                  {/* Name Field */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-2">Name</label>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                      <input
                        type="text"
                        placeholder="John Doe"
                        className="w-full bg-transparent text-white text-sm outline-none placeholder-gray-500"
                        disabled
                      />
                    </div>
                  </div>

                  {/* Email Field */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-2">Email</label>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                      <input
                        type="email"
                        placeholder="john@example.com"
                        className="w-full bg-transparent text-white text-sm outline-none placeholder-gray-500"
                        disabled
                      />
                    </div>
                  </div>

                  {/* Question Type */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-2">Question Type</label>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                      <select className="w-full bg-transparent text-white text-sm outline-none" disabled>
                        <option>Pricing</option>
                        <option>Technical</option>
                        <option>General</option>
                      </select>
                    </div>
                  </div>

                  {/* Message Field */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-2">Your Question</label>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-3">
                      <textarea
                        placeholder="How does Mobius handle risk management?"
                        rows="3"
                        className="w-full bg-transparent text-white text-sm outline-none placeholder-gray-500 resize-none"
                        disabled
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <button
                    className="w-full bg-gradient-to-r from-purple-600 to-purple-500 text-white font-semibold py-3 rounded-lg hover:from-purple-500 hover:to-purple-400 transition-all"
                    disabled
                  >
                    Send Question
                  </button>
                </div>
              </div>
            </div>

            {/* Right Side - Content */}
            <div>
              <div className="inline-block mb-6">
                <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-400 font-medium">
                  Q&A Session
                </span>
              </div>

              <h2 className="text-4xl md:text-5xl font-normal text-white mb-6 leading-tight">
                Get Your Questions Answered
              </h2>

              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                This is your time to ask anything about Mobius, our technology, pricing, or how we can help solve your specific trading challenges. We're here to help you make an informed decision.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Button */}
      <div className="relative z-10 px-6 pb-24">
        <div className="text-center">
          <a
            href="https://calendly.com/dheerajt-uw/15-minute-discovery-call"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-12 py-4 bg-gradient-to-r from-purple-600 to-purple-500 font-semibold rounded-full hover:from-purple-500 hover:to-purple-400 transition-all text-base shadow-lg shadow-purple-500/30"
            style={{ color: '#ffffff' }}
          >
            Book a Discovery Call
          </a>
          <p className="text-sm text-gray-500 mt-4">Free 15-minute consultation • No commitment required</p>
        </div>
      </div>
    </div>
  )
}
