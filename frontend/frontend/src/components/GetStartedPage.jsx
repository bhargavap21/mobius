import { useState, useEffect } from 'react'

export default function GetStartedPage() {
  const [email, setEmail] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [countdown, setCountdown] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  })

  // Countdown timer - set to 120 days from now
  useEffect(() => {
    const targetDate = new Date()
    targetDate.setDate(targetDate.getDate() + 120)

    const updateCountdown = () => {
      const now = new Date()
      const diff = targetDate - now

      if (diff > 0) {
        setCountdown({
          days: Math.floor(diff / (1000 * 60 * 60 * 24)),
          hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((diff % (1000 * 60)) / 1000)
        })
      }
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)

    return () => clearInterval(interval)
  }, [])


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
    <div className="w-full bg-black min-h-screen relative overflow-hidden">
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

      {/* Purple Gradient Background - Mobius Theme */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        {/* Base gradient matching Mobius purple theme */}
        <div
          className="w-full h-full"
          style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(168,85,247,0.3) 0%, rgba(139,92,246,0.2) 30%, rgba(109,40,217,0.1) 60%, rgba(0,0,0,1) 100%)',
          }}
        />
        {/* Grain overlay */}
        <div
          className="absolute inset-0 opacity-[0.05] mix-blend-overlay"
          style={{ backgroundImage: `url('https://grainy-gradients.vercel.app/noise.svg')` }}
        />
      </div>

      {/* Main Waitlist Container */}
      <div className="relative z-10 flex items-center justify-center min-h-screen pt-32 pb-20 px-6">
        <div className="w-full max-w-2xl">
          {/* Waitlist Card */}
          <div className="relative bg-gradient-to-br from-purple-900/30 via-black/40 to-purple-900/30 backdrop-blur-xl rounded-3xl border border-purple-500/20 shadow-2xl shadow-purple-500/10 p-12 overflow-hidden">
            {/* Subtle inner glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-purple-500/5 rounded-3xl pointer-events-none" />

            <div className="relative z-10">
              {/* Title */}
              <h1 className="text-5xl md:text-6xl font-light text-white text-center mb-4 leading-tight">
                Join the waitlist
              </h1>

              {/* Subtitle */}
              <p className="text-lg text-gray-300 text-center mb-12 leading-relaxed">
                Gain exclusive early access to our software and<br />
                stay informed about launch updates
              </p>

              {/* Email Input Section */}
              {!isSubmitted ? (
                <div className="space-y-6 mb-12">
                  <div className="flex items-center gap-3">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleJoinWaitlist()}
                      placeholder="your@email.com"
                      className="flex-1 px-6 py-4 bg-black/40 backdrop-blur-sm text-white placeholder-gray-500 border border-purple-500/30 rounded-xl outline-none focus:border-purple-400/60 transition-colors text-lg"
                    />
                    <button
                      onClick={handleJoinWaitlist}
                      disabled={!email || isLoading}
                      className="px-10 py-4 bg-white text-black font-semibold rounded-xl hover:bg-gray-100 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all text-lg whitespace-nowrap"
                    >
                      {isLoading ? 'Joining...' : 'Get Started'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="mb-12 text-center">
                  <div className="inline-flex items-center gap-3 px-6 py-4 bg-gradient-to-r from-emerald-500/20 to-green-500/20 border border-emerald-500/30 rounded-xl">
                    <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <p className="text-emerald-300 font-semibold text-lg">You're on the waitlist! We'll be in touch soon.</p>
                  </div>
                </div>
              )}

              {/* Social Proof */}
              <div className="flex items-center justify-center gap-4 mb-12">
                <div className="flex -space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 border-2 border-black" />
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 border-2 border-black" />
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-red-400 border-2 border-black" />
                </div>
                <p className="text-gray-400 text-sm">~ 2k+ Peoples already joined</p>
              </div>

              {/* Countdown Timer */}
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-4xl font-light text-white mb-1">{countdown.days}</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider">days</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-light text-white mb-1">{countdown.hours}</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider">hours</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-light text-white mb-1">{countdown.minutes}</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider">minutes</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-light text-white mb-1">{countdown.seconds}</div>
                  <div className="text-sm text-gray-400 uppercase tracking-wider">seconds</div>
                </div>
              </div>
            </div>
          </div>

          {/* Integration Logos Below Card */}
          <div className="mt-16 text-center">
            <p className="text-sm text-gray-500 mb-8 tracking-wide uppercase">
              Integrates with leading platforms
            </p>
            <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
              <span className="text-white text-2xl font-semibold opacity-40 hover:opacity-70 transition-opacity">
                Alpaca
              </span>
              <span className="text-white text-2xl font-bold opacity-40 hover:opacity-70 transition-opacity tracking-tight">
                IBKR
              </span>
              <span className="text-white text-2xl font-semibold opacity-40 hover:opacity-70 transition-opacity">
                Tradier
              </span>
              <span className="text-white text-2xl font-semibold opacity-40 hover:opacity-70 transition-opacity">
                Polygon
              </span>
              <span className="text-white text-2xl font-semibold opacity-40 hover:opacity-70 transition-opacity">
                Finnhub
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
