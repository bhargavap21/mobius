import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import StrategyInput from './components/StrategyInput'
import CodeDisplay from './components/CodeDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import BacktestResults from './components/BacktestResults'
import ProgressIndicator from './components/ProgressIndicator'
import AgentActivityLogPolling from './components/AgentActivityLogPolling'
import Login from './components/Login'
import Signup from './components/Signup'
import BotLibrary from './components/BotLibrary'
import LandingPage from './components/LandingPage'
import StrategySidebar from './components/StrategySidebar'
import './index.css'

function AppContent() {
  const auth = useAuth()
  if (!auth) {
    return <div className="min-h-screen bg-dark-bg flex items-center justify-center text-white">Loading...</div>
  }
  const { user, isAuthenticated, signout, getAuthHeaders } = auth
  const [strategy, setStrategy] = useState(null)
  const [generatedCode, setGeneratedCode] = useState(null)
  const [backtestResults, setBacktestResults] = useState(null)
  const [insightsConfig, setInsightsConfig] = useState(null)  // LLM-generated insights config
  const [sessionId, setSessionId] = useState(null)  // Session ID for progress tracking
  const [loading, setLoading] = useState(false)
  const [backtesting, setBacktesting] = useState(false)
  const [error, setError] = useState(null)
  const [progressSteps, setProgressSteps] = useState([])
  const [currentIteration, setCurrentIteration] = useState(0)
  const [backtestParams, setBacktestParams] = useState({
    takeProfit: 2.0,
    stopLoss: 1.0,
    days: 180,
    initialCapital: 10000
  })

  // Auth modal states
  const [showLogin, setShowLogin] = useState(false)
  const [showSignup, setShowSignup] = useState(false)
  const [showBotLibrary, setShowBotLibrary] = useState(false)
  const [showSidebar, setShowSidebar] = useState(false)

  // Current bot ID for tracking saves/updates
  const [currentBotId, setCurrentBotId] = useState(null)

  // Load last viewed bot on mount (if authenticated)
  useEffect(() => {
    const loadLastBot = async () => {
      if (!isAuthenticated) return

      try {
        const response = await fetch('http://localhost:8000/bots?page=1&page_size=1', {
          headers: getAuthHeaders()
        })

        if (response.ok) {
          const data = await response.json()
          if (data.data && data.data.length > 0) {
            const lastBot = data.data[0]
            setStrategy(lastBot.strategy_config)
            setGeneratedCode(lastBot.generated_code)
            setBacktestResults(lastBot.backtest_results)
            setInsightsConfig(lastBot.insights_config)
            setCurrentBotId(lastBot.id)
            console.log('✅ Loaded last bot:', lastBot.name)
          }
        }
      } catch (err) {
        console.error('Failed to load last bot:', err)
      }
    }

    loadLastBot()
  }, [isAuthenticated, getAuthHeaders])

  // View state - show landing page by default
  const [showLanding, setShowLanding] = useState(true)

  const handleGenerateStrategy = async (userInput, useMultiAgent = true) => {
    setLoading(true)
    setError(null)
    setBacktestResults(null)
    setProgressSteps([])
    setCurrentIteration(0)

    // Generate session ID on frontend first
    const newSessionId = crypto.randomUUID()
    console.log('[App] Generated session ID:', newSessionId)
    setSessionId(newSessionId)
    console.log('[App] Session ID state updated')

    try {
      // Use multi-agent endpoint by default (includes auto-backtesting and refinement)
      const endpoint = useMultiAgent
        ? 'http://localhost:8000/api/strategy/create_multi_agent'
        : 'http://localhost:8000/api/strategy/create'

      // Show initial progress
      if (useMultiAgent) {
        setProgressSteps(['🚀 Starting multi-agent workflow...'])
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_description: userInput,
          session_id: newSessionId  // Pass session ID to backend
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate strategy')
      }

      const data = await response.json()
      setStrategy(data.strategy)
      setGeneratedCode(data.code)

      // Multi-agent endpoint returns backtest results automatically
      if (useMultiAgent && data.backtest_results) {
        setBacktestResults(data.backtest_results)
        setInsightsConfig(data.insights_config)  // Store insights config
        setCurrentIteration(data.iterations)

        // Build progress summary from iteration history
        if (data.iteration_history) {
          const steps = data.iteration_history.map((iter, idx) => {
            const iterNum = idx + 1
            const results = iter.steps.find(s => s.agent === 'BacktestRunner')?.results
            if (results) {
              return `✅ Iteration ${iterNum}: ${results.total_trades} trades, ${results.total_return?.toFixed(1)}% return`
            }
            return `⏳ Iteration ${iterNum}: Processing...`
          })
          setProgressSteps(steps)
        }

        console.log(`✅ Multi-agent workflow completed in ${data.iterations} iterations`)
        if (data.insights_config) {
          console.log(`📊 Generated ${data.insights_config.visualizations?.length || 0} custom visualizations`)
        }

        // Auto-save new bot after generation completes
        setTimeout(() => handleSaveBot(true), 1000)
      }
    } catch (err) {
      console.error('Error during job submission:', err)

      // If we have a session ID, try to retrieve the result
      // (job may have completed even if connection dropped)
      if (newSessionId) {
        console.log('Attempting to retrieve result for session:', newSessionId)
        try {
          const resultResponse = await fetch(`http://localhost:8000/api/strategy/result/${newSessionId}`)
          if (resultResponse.ok) {
            const data = await resultResponse.json()
            console.log('✅ Retrieved completed job result after connection drop')
            setStrategy(data.strategy)
            setGeneratedCode(data.code)
            setBacktestResults(data.backtest_results)
            setInsightsConfig(data.insights_config)
            setCurrentIteration(data.iterations)

            if (data.iteration_history) {
              const steps = data.iteration_history.map((iter, idx) => {
                const iterNum = idx + 1
                const results = iter.steps.find(s => s.agent === 'BacktestRunner')?.results
                if (results) {
                  return `✅ Iteration ${iterNum}: ${results.total_trades} trades, ${results.total_return?.toFixed(1)}% return`
                }
                return `⏳ Iteration ${iterNum}: Processing...`
              })
              setProgressSteps(steps)
            }

            setLoading(false)
            return // Success!
          }
        } catch (retrieveErr) {
          console.log('Result not yet available, will poll...', retrieveErr)
        }
      }

      // Start polling for result
      if (newSessionId && useMultiAgent) {
        console.log('⏱️  Starting polling for job completion...')
        pollForResult(newSessionId)
      } else {
        setError(err.message)
        setLoading(false)
      }
    }
  }

  // Poll for job completion (in case connection dropped)
  const pollForResult = async (sessionId, maxAttempts = 120, intervalMs = 5000) => {
    let attempts = 0

    const poll = async () => {
      attempts++
      console.log(`Polling attempt ${attempts}/${maxAttempts} for session ${sessionId.substring(0, 8)}...`)

      try {
        const response = await fetch(`http://localhost:8000/api/strategy/result/${sessionId}`)
        if (response.ok) {
          const data = await response.json()
          console.log('✅ Job completed! Retrieved result.')

          setStrategy(data.strategy)
          setGeneratedCode(data.code)
          setBacktestResults(data.backtest_results)
          setInsightsConfig(data.insights_config)
          setCurrentIteration(data.iterations)

          if (data.iteration_history) {
            const steps = data.iteration_history.map((iter, idx) => {
              const iterNum = idx + 1
              const results = iter.steps.find(s => s.agent === 'BacktestRunner')?.results
              if (results) {
                return `✅ Iteration ${iterNum}: ${results.total_trades} trades, ${results.total_return?.toFixed(1)}% return`
              }
              return `⏳ Iteration ${iterNum}: Processing...`
            })
            setProgressSteps(steps)
          }

          setLoading(false)
          setError(null)
          return true
        }
      } catch (err) {
        console.log('Still waiting for job completion...')
      }

      // Continue polling
      if (attempts < maxAttempts) {
        setTimeout(poll, intervalMs)
      } else {
        setError('Job is taking longer than expected. Please check back later.')
        setLoading(false)
      }
    }

    poll()
  }

  const handleRunBacktest = async () => {
    if (!strategy) return

    setBacktesting(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/strategy/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy: strategy,
          days: backtestParams.days,
          initial_capital: backtestParams.initialCapital,
          take_profit: backtestParams.takeProfit / 100,
          stop_loss: backtestParams.stopLoss / 100
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to run backtest')
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.error || 'Backtest failed')
      }

      setBacktestResults(data.results)
    } catch (err) {
      setError(err.message)
      console.error('Error:', err)
    } finally {
      setBacktesting(false)
    }
  }

  const handleWorkflowComplete = async (completedSessionId) => {
    console.log('[App] Workflow complete callback triggered for session:', completedSessionId)

    try {
      // Fetch the final results from the backend
      const response = await fetch(`http://localhost:8000/api/strategy/result/${completedSessionId}`)

      if (response.ok) {
        const data = await response.json()
        console.log('[App] ✅ Retrieved completed job result')

        // Set all the state from the completed job
        setStrategy(data.strategy)
        setGeneratedCode(data.code)
        setBacktestResults(data.backtest_results)
        setInsightsConfig(data.insights_config)
        setCurrentIteration(data.iterations)

        if (data.iteration_history) {
          const steps = data.iteration_history.map((iter, idx) => {
            const iterNum = idx + 1
            const results = iter.steps.find(s => s.agent === 'BacktestRunner')?.results
            if (results) {
              return `✅ Iteration ${iterNum}: ${results.total_trades} trades, ${results.total_return?.toFixed(1)}% return`
            }
            return `⏳ Iteration ${iterNum}: Processing...`
          })
          setProgressSteps(steps)
        }

        setLoading(false)
      } else {
        console.error('[App] Failed to retrieve result:', response.status)
        setError('Failed to retrieve completed results')
        setLoading(false)
      }
    } catch (err) {
      console.error('[App] Error fetching completed results:', err)
      setError('Error retrieving results: ' + err.message)
      setLoading(false)
    }
  }

  const handleReset = () => {
    setStrategy(null)
    setGeneratedCode(null)
    setBacktestResults(null)
    setError(null)
    setShowLanding(true)
    setCurrentBotId(null)
  }

  const handleSaveBot = async (autoSave = false) => {
    if (!isAuthenticated) {
      if (!autoSave) setShowLogin(true)
      return
    }

    if (!strategy || !generatedCode) {
      return
    }

    try {
      // If we have a current bot ID, update it instead of creating new
      if (currentBotId) {
        const response = await fetch(`http://localhost:8000/bots/${currentBotId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders(),
          },
          body: JSON.stringify({
            strategy_config: strategy,
            generated_code: generatedCode,
            backtest_results: backtestResults,
            insights_config: insightsConfig,
            session_id: sessionId,
          }),
        })

        if (!response.ok) {
          throw new Error('Failed to update bot')
        }

        if (!autoSave) {
          alert('Bot updated successfully!')
        }
        console.log('✅ Bot auto-saved')
        return
      }

      // Create new bot
      const botName = autoSave
        ? `${strategy.asset} ${strategy.strategy_type} Bot`
        : prompt('Enter a name for this bot:', `${strategy.asset} ${strategy.strategy_type} Bot`)

      if (!botName) return

      const response = await fetch('http://localhost:8000/bots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          name: botName,
          description: `${strategy.strategy_type} strategy for ${strategy.asset}`,
          strategy_config: strategy,
          generated_code: generatedCode,
          backtest_results: backtestResults,
          insights_config: insightsConfig,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to save bot')
      }

      const data = await response.json()
      setCurrentBotId(data.id)

      if (!autoSave) {
        alert('Bot saved successfully!')
      }
      console.log('✅ Bot saved with ID:', data.id)
    } catch (err) {
      console.error('Error saving bot:', err)
      if (!autoSave) {
        setError('Failed to save bot: ' + err.message)
      }
    }
  }

  const handleLoadBot = (botData) => {
    setStrategy(botData.strategy)
    setGeneratedCode(botData.code)
    setBacktestResults(botData.backtest_results)
    setInsightsConfig(botData.insights_config)
    setCurrentBotId(botData.id)
    setShowBotLibrary(false)
    console.log('✅ Loaded bot:', botData.name)
  }

  const handleRefineStrategy = async (refinementPrompt) => {
    // Close the sidebar
    setShowSidebar(false)

    // Clear previous results but keep the old strategy visible
    setLoading(true)
    setError(null)

    // Generate new session ID
    const newSessionId = crypto.randomUUID()
    setSessionId(newSessionId)

    try {
      // Call the NEW refine endpoint instead of recreating from scratch
      const response = await fetch('http://localhost:8000/api/strategy/refine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_strategy: strategy,
          current_code: generatedCode,
          refinement_instructions: refinementPrompt,
          session_id: newSessionId
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to refine strategy')
      }

      const data = await response.json()
      setStrategy(data.strategy)
      setGeneratedCode(data.code)
      setBacktestResults(data.backtest_results)
      setInsightsConfig(data.insights_config)

      console.log('✅ Strategy refined successfully:', data.changes_made)
      setLoading(false)

      // Auto-save after refinement
      setTimeout(() => handleSaveBot(true), 1000)
    } catch (err) {
      console.error('Error during refinement:', err)

      // Try polling for result if connection dropped
      if (newSessionId) {
        pollForResult(newSessionId)
      } else {
        setError(err.message)
        setLoading(false)
      }
    }
  }

  const handleGetStarted = () => {
    setShowLanding(false)
  }

  // Show landing page if user hasn't started
  if (showLanding && !generatedCode && !loading) {
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

              <div className="flex items-center gap-3">
                {isAuthenticated ? (
                  <>
                    <button
                      onClick={() => setShowBotLibrary(true)}
                      className="btn btn-secondary text-sm"
                    >
                      📚 My Bots
                    </button>
                    <div className="flex items-center gap-2 pl-3 border-l border-gray-700">
                      <span className="text-sm text-gray-400">{user?.email}</span>
                      <button
                        onClick={signout}
                        className="text-sm text-gray-400 hover:text-white"
                      >
                        Sign Out
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => setShowLogin(true)}
                      className="btn btn-secondary text-sm"
                    >
                      Sign In
                    </button>
                    <button
                      onClick={() => setShowSignup(true)}
                      className="btn btn-primary text-sm"
                    >
                      Sign Up
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        <LandingPage onGetStarted={handleGetStarted} />

        {/* Footer */}
        <footer className="border-t border-dark-border py-6">
          <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-500">
            <p>Built for DubHacks 2025 • Powered by Claude AI & Alpaca</p>
          </div>
        </footer>

        {/* Auth Modals */}
        {showLogin && (
          <Login
            onClose={() => setShowLogin(false)}
            onSwitchToSignup={() => {
              setShowLogin(false)
              setShowSignup(true)
            }}
          />
        )}

        {showSignup && (
          <Signup
            onClose={() => setShowSignup(false)}
            onSwitchToLogin={() => {
              setShowSignup(false)
              setShowLogin(true)
            }}
          />
        )}

        {/* Bot Library Modal */}
        {showBotLibrary && (
          <BotLibrary
            onClose={() => setShowBotLibrary(false)}
            onLoadBot={(botData) => {
              handleLoadBot(botData)
              setShowLanding(false)
            }}
          />
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg flex flex-col">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-surface/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="px-12 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowLanding(true)}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-accent-primary to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🤖</span>
              </div>
              <div className="text-left">
                <h1 className="text-xl font-bold text-white">AI Trading Bot Generator</h1>
                <p className="text-xs text-gray-400">Transform strategies into code with AI</p>
              </div>
            </button>

            <div className="flex items-center gap-3">
              {isAuthenticated ? (
                <>
                  <button
                    onClick={() => setShowBotLibrary(true)}
                    className="btn btn-secondary text-sm"
                  >
                    📚 My Bots
                  </button>
                  {generatedCode && backtestResults && (
                    <button
                      onClick={handleSaveBot}
                      className="btn btn-primary text-sm"
                    >
                      💾 Save Bot
                    </button>
                  )}
                  {generatedCode && (
                    <button
                      onClick={handleReset}
                      className="btn btn-secondary text-sm"
                    >
                      New Strategy
                    </button>
                  )}
                  <div className="flex items-center gap-2 pl-3 border-l border-gray-700">
                    <span className="text-sm text-gray-400">{user?.email}</span>
                    <button
                      onClick={signout}
                      className="text-sm text-gray-400 hover:text-white"
                    >
                      Sign Out
                    </button>
                  </div>
                </>
              ) : (
                <>
                  {generatedCode && (
                    <button
                      onClick={handleReset}
                      className="btn btn-secondary text-sm"
                    >
                      New Strategy
                    </button>
                  )}
                  <button
                    onClick={() => setShowLogin(true)}
                    className="btn btn-secondary text-sm"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => setShowSignup(true)}
                    className="btn btn-primary text-sm"
                  >
                    Sign Up
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-2xl w-full px-6">
              <div className="mb-6">
                <LoadingSpinner />
                <p className="text-gray-400 mt-4 text-lg font-semibold">
                  🤖 Multi-Agent System Working...
                </p>
                <p className="text-gray-500 text-sm mt-2">
                  Iterating through code generation, backtesting, and analysis
                </p>
              </div>

              {/* Real-time Agent Activity Log */}
              {sessionId && (
                <div className="mt-6">
                  <AgentActivityLogPolling
                    sessionId={sessionId}
                    onComplete={handleWorkflowComplete}
                  />
                </div>
              )}

              {/* Fallback animated indicator if no session ID */}
              {!sessionId && <ProgressIndicator />}
            </div>
          </div>
        ) : !generatedCode ? (
          <div className="max-w-7xl mx-auto px-6 py-8 w-full">
            <StrategyInput onGenerate={handleGenerateStrategy} />
          </div>
        ) : (
          <div className="flex flex-1 gap-0 overflow-hidden">
            {/* Main Content */}
            <div className="flex-1 overflow-y-auto px-12 py-8 max-w-[1600px]">
            {error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
                <p className="font-medium">Error</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            )}

            <div className="space-y-6">
            {/* Strategy Summary */}
            {strategy && (
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">📋 Strategy Overview</h2>
                  <button
                    onClick={handleRunBacktest}
                    disabled={backtesting}
                    className="btn btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {backtesting ? (
                      <>
                        <svg className="animate-spin h-4 w-4 inline mr-2" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Running...
                      </>
                    ) : (
                      <>📊 Run Backtest</>
                    )}
                  </button>
                </div>
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

            {/* Backtest Results */}
            {backtestResults && (
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">📊 Backtest Results</h2>
                  <button
                    onClick={() => setShowSidebar(true)}
                    className="btn btn-secondary text-sm"
                  >
                    🔧 Refine Strategy
                  </button>
                </div>
                <BacktestResults results={backtestResults} insightsConfig={insightsConfig} />
              </div>
            )}

            {/* Generated Code */}
            <CodeDisplay code={generatedCode} strategyName={strategy?.name} />
            </div>
            </div>

            {/* Strategy Sidebar - part of page layout */}
            <StrategySidebar
              isOpen={showSidebar}
              onClose={() => setShowSidebar(false)}
              currentStrategy={strategy}
              onRefineStrategy={handleRefineStrategy}
              onRunBacktest={handleRunBacktest}
            />
          </div>
        )}
      </main>

      {/* Auth Modals */}
      {showLogin && (
        <Login
          onClose={() => setShowLogin(false)}
          onSwitchToSignup={() => {
            setShowLogin(false)
            setShowSignup(true)
          }}
        />
      )}

      {showSignup && (
        <Signup
          onClose={() => setShowSignup(false)}
          onSwitchToLogin={() => {
            setShowSignup(false)
            setShowLogin(true)
          }}
        />
      )}

      {/* Bot Library Modal */}
      {showBotLibrary && (
        <BotLibrary
          onClose={() => setShowBotLibrary(false)}
          onLoadBot={handleLoadBot}
        />
      )}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
