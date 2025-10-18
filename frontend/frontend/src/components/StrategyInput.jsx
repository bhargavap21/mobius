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
        <h2 className="text-4xl md:text-5xl font-light text-fg mb-3 leading-tight">
          Describe Your Trading Strategy
        </h2>
        <p className="text-lg text-fg-muted">
          Use plain English to create a professional trading bot in seconds
        </p>
      </div>

      {/* Examples */}
      <div className="mb-6">
        <p className="text-sm text-fg-muted mb-3">Try an example:</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {EXAMPLE_STRATEGIES.map((example, idx) => (
            <button
              key={idx}
              onClick={() => loadExample(example)}
              className="rounded-2xl border border-line bg-white/5 p-4 text-left text-fg hover:bg-white/7 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-400 transition-colors group"
            >
              <h3 className="text-sm font-medium group-hover:text-accent transition-colors mb-1">
                {example.title}
              </h3>
              <p className="text-xs text-fg-muted line-clamp-2">
                {example.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="rounded-2xl bg-white/5 p-6">
          <label htmlFor="strategy" className="mb-2 block text-sm font-medium text-fg">
            Strategy Description
          </label>
          <textarea
            id="strategy"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Example: Buy TSLA when Elon Musk tweets positively about Tesla and the stock is below $500. Sell at +2% profit or -1% stop loss."
            className="min-h-[180px] w-full rounded-2xl border border-line bg-white/5 p-4 text-fg placeholder:text-fg-muted focus:ring-2 focus:ring-accent-400 focus:outline-none resize-none"
            required
          />

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-fg-muted">
              {input.length} characters
            </p>
            <button
              type="submit"
              disabled={!input.trim() || isGenerating}
              aria-busy={isGenerating}
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-accent-dark px-5 py-3 font-medium text-white shadow-md transition hover:bg-accent disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-400"
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
                  Generating…
                </>
              ) : (
                'Generate Trading Bot'
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
