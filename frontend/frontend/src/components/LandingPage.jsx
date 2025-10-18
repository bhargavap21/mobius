import { Sparkles, Zap, TrendingUp, Code, BarChart3, Brain, ArrowRight, Check } from 'lucide-react'

export default function LandingPage({ onGetStarted }) {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered Strategy Generation",
      description: "Transform natural language into production-ready trading algorithms using advanced AI"
    },
    {
      icon: BarChart3,
      title: "Automated Backtesting",
      description: "Validate strategies with historical data and get instant performance metrics"
    },
    {
      icon: Code,
      title: "Clean Python Code",
      description: "Export professional, well-documented code ready for deployment"
    },
    {
      icon: Zap,
      title: "Multi-Agent Refinement",
      description: "AI agents collaborate to optimize and improve your strategy automatically"
    },
    {
      icon: TrendingUp,
      title: "Real-Time Market Data",
      description: "Connect to live market feeds and social sentiment analysis"
    },
    {
      icon: Sparkles,
      title: "Custom Visualizations",
      description: "Dynamic charts and insights generated specifically for your strategy"
    }
  ]

  const benefits = [
    "No coding required - just describe your strategy",
    "Backtested on real market data",
    "Multi-agent AI optimization",
    "Export production-ready code",
    "Save and manage bot library",
    "Social sentiment integration"
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-dark-bg via-dark-bg to-dark-surface">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Gradient Orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 -left-1/4 w-1/2 h-1/2 bg-accent-primary/20 rounded-full blur-[128px] animate-pulse-slow" />
          <div className="absolute bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-blue-600/20 rounded-full blur-[128px] animate-pulse-slow" style={{ animationDelay: '1s' }} />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 pt-20 pb-24 md:pt-32 md:pb-32">
          <div className="text-center max-w-4xl mx-auto animate-fade-in-up">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent-primary/10 border border-accent-primary/20 mb-8">
              <Sparkles className="w-4 h-4 text-accent-primary" />
              <span className="text-sm font-medium text-accent-primary">Built for DubHacks 2025</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              Transform Ideas Into
              <span className="block bg-gradient-to-r from-accent-primary via-blue-500 to-purple-500 bg-clip-text text-transparent">
                Trading Algorithms
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed">
              Describe your trading strategy in plain English. Our AI agents generate, backtest, and optimize production-ready code in minutes.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={onGetStarted}
                className="group relative px-8 py-4 bg-gradient-to-r from-accent-primary to-blue-600 rounded-xl font-semibold text-white text-lg shadow-lg shadow-accent-primary/25 hover:shadow-accent-primary/40 transition-all duration-300 hover:scale-105"
              >
                <span className="flex items-center gap-2">
                  Start Building Free
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </button>
              <button
                onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                className="px-8 py-4 bg-dark-surface/50 backdrop-blur-sm border border-dark-border rounded-xl font-semibold text-white text-lg hover:bg-dark-surface transition-all duration-300"
              >
                See How It Works
              </button>
            </div>

            {/* Stats */}
            <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">3+</div>
                <div className="text-sm text-gray-400">AI Agents</div>
              </div>
              <div className="text-center border-x border-dark-border">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">&lt;5min</div>
                <div className="text-sm text-gray-400">Generation Time</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">100%</div>
                <div className="text-sm text-gray-400">Code Quality</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="relative py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 animate-fade-in-up">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Everything You Need to Build
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Powered by multi-agent AI systems and real market data
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="group relative p-6 bg-dark-surface/50 backdrop-blur-sm border border-dark-border rounded-2xl hover:border-accent-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-accent-primary/10 animate-fade-in-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="w-12 h-12 bg-gradient-to-br from-accent-primary/20 to-blue-600/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-accent-primary" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative py-24 px-6 bg-dark-surface/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 animate-fade-in-up">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Simple 3-Step Process
            </h2>
            <p className="text-xl text-gray-400">
              From idea to production in minutes
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Describe Your Strategy",
                description: "Use natural language to explain your trading idea. No technical knowledge required."
              },
              {
                step: "02",
                title: "AI Generates & Tests",
                description: "Multi-agent system creates code, backtests it, and automatically refines the strategy."
              },
              {
                step: "03",
                title: "Export & Deploy",
                description: "Get production-ready Python code with documentation, ready to run on any platform."
              }
            ].map((item, index) => (
              <div
                key={item.step}
                className="relative animate-fade-in-up"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div className="text-6xl font-bold bg-gradient-to-br from-accent-primary/20 to-transparent bg-clip-text text-transparent mb-4">
                  {item.step}
                </div>
                <h3 className="text-2xl font-semibold text-white mb-3">
                  {item.title}
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="relative py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in-up">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Built for Traders & Developers
              </h2>
              <p className="text-xl text-gray-400 mb-8">
                Whether you're a seasoned quant or just starting out, our platform makes algorithmic trading accessible to everyone.
              </p>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div
                    key={benefit}
                    className="flex items-start gap-3 animate-fade-in-up"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="w-6 h-6 bg-accent-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="w-4 h-4 text-accent-primary" />
                    </div>
                    <span className="text-gray-300">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="relative bg-gradient-to-br from-dark-surface to-dark-bg border border-dark-border rounded-2xl p-8 shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/10 to-blue-600/10 rounded-2xl" />
                <div className="relative">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-red-500 rounded-full" />
                    <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                  </div>
                  <pre className="text-sm text-gray-300 overflow-x-auto">
                    <code>{`# Generated Trading Bot
import alpaca_trade_api as tradeapi

class TradingBot:
    def __init__(self):
        self.api = tradeapi.REST()

    def analyze_market(self):
        # AI-generated strategy
        sentiment = get_sentiment()
        price = get_current_price()

        if sentiment > 0.7:
            self.execute_trade('buy')

    def execute_trade(self, action):
        # Execute with risk management
        ...`}</code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative bg-gradient-to-br from-accent-primary/10 to-blue-600/10 border border-accent-primary/20 rounded-3xl p-12 overflow-hidden animate-fade-in-up">
            <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/5 to-transparent" />
            <div className="relative">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Ready to Build Your First Bot?
              </h2>
              <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                Join the future of algorithmic trading. No credit card required.
              </p>
              <button
                onClick={onGetStarted}
                className="group px-10 py-5 bg-gradient-to-r from-accent-primary to-blue-600 rounded-xl font-semibold text-white text-lg shadow-lg shadow-accent-primary/25 hover:shadow-accent-primary/40 transition-all duration-300 hover:scale-105"
              >
                <span className="flex items-center gap-2">
                  Get Started Now
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
