import { useState } from 'react'
import StrategyInput from './components/StrategyInput'
import CodeDisplay from './components/CodeDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import './index.css'

function App() {
  const [strategy, setStrategy] = useState(null)
  const [generatedCode, setGeneratedCode] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerateStrategy = async (userInput) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/strategy/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ strategy_description: userInput }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate strategy')
      }

      const data = await response.json()
      setStrategy(data.strategy)
      setGeneratedCode(data.code)
    } catch (err) {
      setError(err.message)
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setStrategy(null)
    setGeneratedCode(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-surface/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-accent-primary to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🤖</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AI Trading Bot Generator</h1>
                <p className="text-xs text-gray-400">Transform strategies into code with AI</p>
              </div>
            </div>
            {generatedCode && (
              <button
                onClick={handleReset}
                className="btn btn-secondary text-sm"
              >
                New Strategy
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <LoadingSpinner />
          </div>
        ) : !generatedCode ? (
          <StrategyInput onGenerate={handleGenerateStrategy} />
        ) : (
          <div className="space-y-6">
            {/* Strategy Summary */}
            {strategy && (
              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-4">📋 Strategy Overview</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Asset</p>
                    <p className="text-lg font-semibold text-accent-primary">{strategy.asset}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Take Profit</p>
                    <p className="text-lg font-semibold text-accent-success">
                      +{(strategy.exit_conditions?.take_profit * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Stop Loss</p>
                    <p className="text-lg font-semibold text-accent-danger">
                      -{(strategy.exit_conditions?.stop_loss * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-dark-border">
                  <p className="text-sm text-gray-400 mb-2">Data Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {strategy.data_sources?.map((source) => (
                      <span
                        key={source}
                        className="px-3 py-1 bg-dark-bg rounded-full text-sm text-gray-300 border border-dark-border"
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Generated Code */}
            <CodeDisplay code={generatedCode} strategyName={strategy?.name} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-border mt-12 py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-500">
          <p>Built for DubHacks 2025 • Powered by Claude AI & Alpaca</p>
        </div>
      </footer>
    </div>
  )
}

export default App
