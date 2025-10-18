import { Brain, Zap, Code, BarChart3, TrendingUp, Check } from 'lucide-react'

export default function LandingPage() {
  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="w-full">
      {/* Hero Section with 3D */}
      <section className="w-full h-screen overflow-hidden relative bg-black">
        <div className="max-w-7xl mx-auto h-full px-6 flex items-center">
          {/* Left side - Text */}
          <div className="w-1/2 z-10">
            <h1 className="text-6xl md:text-7xl font-light text-white mb-6 leading-tight">
              AI-Powered Trading from <span className="italic font-serif">Strategy to Deployment</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 leading-relaxed">
              Mobius delivers proven algorithms, automated backtesting, and production-ready code to traders, quants, and developers.
            </p>
          </div>

          {/* Right side - 3D Book */}
          <div className="w-1/2 h-full absolute right-0 top-0">
            <iframe
              src="https://my.spline.design/untitled-d60805fcfc4322f8deb736b6722c1f49/"
              width="100%"
              height="100%"
              className="w-full h-full border-0"
              title="3D Trading Bot Visualization"
            />
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce">
          <button
            onClick={() => scrollToSection('process')}
            className="w-6 h-10 border-2 border-white/30 rounded-full flex items-start justify-center p-2 hover:border-white/50 transition-colors"
          >
            <div className="w-1 h-3 bg-white/50 rounded-full" />
          </button>
        </div>
      </section>

      {/* Process Section */}
      <section id="process" className="bg-black py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="border border-blue-500/30 rounded-3xl p-12 relative">
            {/* Header */}
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-gray-800/50 rounded-full text-sm text-gray-400 mb-6">
                Process
              </div>
              <h2 className="text-5xl md:text-6xl font-light text-white mb-4">
                Trading bots, <span className="italic font-serif">effortlessly.</span>
              </h2>
              <p className="text-xl text-gray-400">
                Build production-ready algorithms in three effortless steps.
              </p>
            </div>

            {/* Steps */}
            <div className="grid md:grid-cols-3 gap-12 mb-12">
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <div className="h-12 flex items-center justify-center mb-3">
                  <h3 className="text-2xl font-light text-white">Describe</h3>
                </div>
                <p className="text-gray-400 leading-relaxed">
                  Tell us your trading strategy in plain English. No coding knowledge required.
                </p>
              </div>

              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="h-12 flex items-center justify-center mb-3">
                  <h3 className="text-2xl font-light text-white">Generate</h3>
                </div>
                <p className="text-gray-400 leading-relaxed">
                  AI agents create, backtest, and optimize your bot in minutes.
                </p>
              </div>

              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </div>
                <div className="h-12 flex flex-col items-center justify-center mb-3">
                  <div className="flex justify-center gap-1 mb-2">
                    <span className="text-white text-2xl">★</span>
                    <span className="text-white text-2xl">★</span>
                    <span className="text-white text-2xl">★</span>
                  </div>
                  <h3 className="text-2xl font-light text-white">Deploy</h3>
                </div>
                <p className="text-gray-400 leading-relaxed">
                  Download production-ready code and deploy to any trading platform.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-black py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="border border-blue-500/30 rounded-3xl p-12 relative">
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-gray-800/50 rounded-full text-sm text-gray-400 mb-6">
                Features
              </div>
              <h2 className="text-5xl md:text-6xl font-light text-white mb-4">
                Powerful <span className="italic font-serif">Features.</span>
              </h2>
              <p className="text-xl text-gray-400">
                Everything you need to build profitable trading algorithms.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: Brain,
                  title: "AI-Powered Generation",
                  description: "Advanced AI transforms your natural language descriptions into sophisticated trading algorithms"
                },
                {
                  icon: BarChart3,
                  title: "Automated Backtesting",
                  description: "Validate strategies against historical market data with comprehensive performance metrics"
                },
                {
                  icon: Code,
                  title: "Clean Python Code",
                  description: "Export professional, well-documented code ready for immediate deployment"
                },
                {
                  icon: Zap,
                  title: "Multi-Agent Refinement",
                  description: "Multiple AI agents collaborate to optimize and improve your strategy automatically"
                },
                {
                  icon: TrendingUp,
                  title: "Real-Time Market Data",
                  description: "Integration with Alpaca for live market feeds and social sentiment analysis"
                },
                {
                  icon: Check,
                  title: "Custom Visualizations",
                  description: "Dynamic charts and performance insights generated specifically for your strategy"
                }
              ].map((feature) => (
                <div key={feature.title} className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <feature.icon className="w-12 h-12 text-white" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-xl font-light text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed text-sm">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-gradient-to-b from-dark-bg to-dark-surface py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-5xl md:text-6xl font-light text-white mb-6">
                Built for Everyone
              </h2>
              <p className="text-xl text-gray-400 mb-8">
                Whether you're a seasoned quant trader or just starting out, our platform makes algorithmic trading accessible to everyone.
              </p>
              <div className="space-y-4">
                {[
                  "No coding required - just describe your strategy",
                  "Backtested on real market data",
                  "Multi-agent AI optimization",
                  "Export production-ready code",
                  "Save and manage bot library",
                  "Social sentiment integration",
                  "Free to get started"
                ].map((benefit) => (
                  <div key={benefit} className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-accent-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="w-4 h-4 text-accent-primary" />
                    </div>
                    <span className="text-gray-300">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="relative bg-gradient-to-br from-dark-surface to-dark-bg border border-dark-border rounded-2xl p-8 shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/10 to-blue-600/10 rounded-2xl" />
                <div className="relative">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-red-500 rounded-full" />
                    <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                  </div>
                  <pre className="text-sm text-gray-300 overflow-x-auto">
                    <code>{`# AI-Generated Trading Bot
import alpaca_trade_api as tradeapi
from sentiment_analyzer import analyze

class TradingBot:
    def __init__(self):
        self.api = tradeapi.REST()

    def analyze_market(self):
        # Get market sentiment
        sentiment = analyze()
        price = self.get_price()

        # Execute strategy
        if sentiment > 0.7 and price > sma:
            self.execute_trade('buy')

    def execute_trade(self, action):
        # Risk management included
        position_size = self.calculate_size()
        self.api.submit_order(...)
        `}</code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
