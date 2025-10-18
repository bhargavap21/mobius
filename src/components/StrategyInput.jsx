import { useState } from 'react'

const EXAMPLE_STRATEGIES = [
  {
    title: "Elon Tweet Strategy 🚀",
    description: "Buy TSLA when Elon Musk tweets something positive about Tesla. Sell at +2% profit or -1% stop loss."
  },
  {
    title: "Reddit Sentiment",
    description: "Buy GME when r/wallstreetbets sentiment is bullish (> 0.5). Sell at +5% profit or -2% stop loss."
  },
  {
    title: "Technical Indicator",
    description: "Buy AAPL when RSI drops below 30. Sell when RSI goes above 70 or at -1% stop loss."
  },
]

export default function StrategyInput({ onGenerate }) {
  const [input, setInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    setIsGenerating(true)
    await onGenerate(input)
    setIsGenerating(false)
  }

  const loadExample = (example) => {
    setInput(example.description)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-3">
          Describe Your Trading Strategy
        </h2>
        <p className="text-gray-400">
          Use plain English to create a professional trading bot in seconds
        </p>
      </div>

      {/* Examples */}
      <div className="mb-6">
        <p className="text-sm text-gray-400 mb-3">Try an example:</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {EXAMPLE_STRATEGIES.map((example, idx) => (
            <button
              key={idx}
              onClick={() => loadExample(example)}
              className="card text-left hover:border-accent-primary transition-colors group"
            >
              <h3 className="font-medium text-white group-hover:text-accent-primary transition-colors mb-1">
                {example.title}
              </h3>
              <p className="text-xs text-gray-400 line-clamp-2">
                {example.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="card">
          <label htmlFor="strategy" className="block text-sm font-medium text-gray-300 mb-2">
            Strategy Description
          </label>
          <textarea
            id="strategy"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Example: Buy TSLA when Elon Musk tweets positively about Tesla and the stock is below $500. Sell at +2% profit or -1% stop loss."
            className="textarea w-full h-40"
            required
          />

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {input.length} characters
            </p>
            <button
              type="submit"
              disabled={!input.trim() || isGenerating}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <span>✨</span>
                  Generate Trading Bot
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Features */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
        <div className="p-4">
          <div className="text-2xl mb-2">⚡</div>
          <p className="text-sm font-medium text-gray-300">Instant Generation</p>
          <p className="text-xs text-gray-500 mt-1">Code ready in seconds</p>
        </div>
        <div className="p-4">
          <div className="text-2xl mb-2">🎯</div>
          <p className="text-sm font-medium text-gray-300">Production Ready</p>
          <p className="text-xs text-gray-500 mt-1">Clean, tested code</p>
        </div>
        <div className="p-4">
          <div className="text-2xl mb-2">🤖</div>
          <p className="text-sm font-medium text-gray-300">AI Powered</p>
          <p className="text-xs text-gray-500 mt-1">Claude Sonnet 4.5</p>
        </div>
      </div>
    </div>
  )
}
