import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import StrategyInput from './components/StrategyInput'
import CodeDisplay from './components/CodeDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import BacktestResults from './components/BacktestResults'
import ProgressIndicator from './components/ProgressIndicator'
import AgentActivityLogWS from './components/AgentActivityLogWS'
import Login from './components/Login'
import Signup from './components/Signup'
import BotLibrary from './components/BotLibrary'
import LandingPage from './components/LandingPage'
import RefineSidebar from './components/RefineSidebar'
import DeploymentPage from './components/DeploymentPage'
import DeploymentMonitor from './components/DeploymentMonitor'
import ChatHistorySidebar from './components/ChatHistorySidebar'
import SessionExpiredModal from './components/SessionExpiredModal'
import './index.css'

function AppContent() {
  const auth = useAuth()
  if (!auth) {
    return <div className="min-h-screen bg-dark-bg flex items-center justify-center text-white">Loading...</div>
  }
  const { user, isAuthenticated, signout, getAuthHeaders, tokenExpiredError, handleTokenExpired, clearExpiredError } = auth
  const navigate = useNavigate()
  const location = useLocation()
  const [strategy, setStrategy] = useState(null)
  const [generatedCode, setGeneratedCode] = useState(null)
  const [backtestResults, setBacktestResults] = useState(null)
  const [insightsConfig, setInsightsConfig] = useState(null)  // LLM-generated insights config
  const [sessionId, setSessionId] = useState(null)  // Session ID for progress tracking
  const [loading, setLoading] = useState(false)
  const [backtesting, setBacktesting] = useState(false)
  const [error, setError] = useState(null)
  const [refinementStatus, setRefinementStatus] = useState(null)  // 'refining', 'success', 'error', null
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

  // Current bot ID for tracking saves/updates
  const [currentBotId, setCurrentBotId] = useState(null)

  // Sidebar open state
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Deployment page state
  const [showDeploymentPage, setShowDeploymentPage] = useState(false)
  const [showDeploymentMonitor, setShowDeploymentMonitor] = useState(false)

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
          if (data.items && data.items.length > 0) {
            const lastBot = data.items[0]
            setStrategy(lastBot.strategy_config)
            setGeneratedCode(lastBot.generated_code)
            setBacktestResults(lastBot.backtest_results)
            setInsightsConfig(lastBot.insights_config)
            setCurrentBotId(lastBot.id)
            console.log('Loaded last bot:', lastBot.name)
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
  const [fastMode, setFastMode] = useState(false)

  const handleGenerateStrategy = async (userInput, useMultiAgent = true, useFastMode = false) => {
    // Check authentication first before starting generation
    if (!isAuthenticated || !user) {
      handleTokenExpired()
      return
    }

    setLoading(true)
    setError(null)
    setBacktestResults(null)
    setProgressSteps([])
    setCurrentIteration(0)

    try {
      // STEP 1: Create session (no work starts yet)
      console.log('[App] Step 1: Creating session...')
      const sessionResponse = await fetch('http://localhost:8000/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      })

      if (!sessionResponse.ok) {
        throw new Error(`Failed to create session: ${sessionResponse.status}`)
      }

      const { sessionId: newSessionId } = await sessionResponse.json()
      console.log('[App] ✅ Session created:', newSessionId)

      // STEP 2: Set sessionId to mount SSE component (which will open stream)
      setSessionId(newSessionId)

      // STEP 3: Wait for SSE ready signal, then start workflow
      // We'll use a Promise that resolves when the SSE component signals ready
      await new Promise((resolve) => {
        let resolved = false

        window.wsStreamReady = (sid) => {
          if (sid === newSessionId && !resolved) {
            resolved = true
            console.log('[App] ✅ WebSocket stream ready, starting workflow...')
            resolve()
          }
        }

        // Timeout after 5 seconds in case WebSocket doesn't connect
        setTimeout(() => {
          if (!resolved) {
            resolved = true
            console.warn('[App] ⚠️ WebSocket ready timeout, starting workflow anyway')
            resolve()
          }
        }, 5000)
      })

      // STEP 3: Start the workflow (SSE stream is now open and waiting)
      console.log('[App] Step 3: Starting workflow...')
      const startUrl = useFastMode
        ? `http://localhost:8000/api/sessions/${newSessionId}/start?fast_mode=true`
        : `http://localhost:8000/api/sessions/${newSessionId}/start`

      const startResponse = await fetch(startUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({
          strategy_description: userInput
        }),
      })

      console.log(`[App] Workflow started: ${startResponse.status} ${startResponse.statusText}`)

      // Check for 401/403 Unauthorized (expired token)
      if (startResponse.status === 401 || startResponse.status === 403) {
        setLoading(false)
        handleTokenExpired()
        return
      }

      if (!startResponse.ok) {
        const errorText = await startResponse.text()
        console.error(`[App] Request failed:`, errorText)
        throw new Error(`Failed to start workflow (${startResponse.status}): ${errorText}`)
      }

      console.log('[App] ✅ Workflow started successfully, waiting for WebSocket events...')
      // Note: Results will be handled by onWorkflowComplete callback when WebSocket signals completion

    } catch (err) {
      console.error('❌ Error during strategy generation:', err)
      setError(err.message || 'Failed to generate strategy')
      setLoading(false)
      setSessionId(null)
    }
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
        console.log('[App] Retrieved completed job result')

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
              return `Iteration ${iterNum}: ${results.total_trades} trades, ${results.total_return?.toFixed(1)}% return`
            }
            return `Iteration ${iterNum}: Processing...`
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

  const handleSignOut = () => {
    signout()
    setShowLanding(true)
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
        console.log('Bot auto-saved')
        return
      }

      // Create new bot
      const botName = autoSave
        ? `${strategy.asset} ${strategy.strategy_type} Bot`
        : prompt('Enter a name for this bot:', `${strategy.asset} ${strategy.strategy_type} Bot`)

      if (!botName) return

      console.log('Attempting to save bot:')
      console.log('  Name:', botName)
      console.log('  Strategy:', strategy)
      console.log('  Session ID:', sessionId)

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
        // Log detailed error information
        const errorText = await response.text()
        console.error('Bot save failed:')
        console.error('  Status:', response.status, response.statusText)
        console.error('  Response:', errorText)

        // Check for 401/403 Unauthorized (expired token)
        if (response.status === 401 || response.status === 403) {
          handleTokenExpired()
          return
        }
        throw new Error(`Failed to save bot (${response.status}): ${errorText}`)
      }

      const data = await response.json()
      setCurrentBotId(data.id)

      // Always show success confirmation
      alert('Bot saved successfully!')
      console.log('Bot saved with ID:', data.id)
    } catch (err) {
      console.error('Error saving bot:', err)
      if (!autoSave) {
        setError('Failed to save bot: ' + err.message)
      }
    }
  }

  const handleLoadBot = (botData) => {
    // Handle both transformed (from BotLibrary) and raw (from API) formats
    setStrategy(botData.strategy || botData.strategy_config)
    setGeneratedCode(botData.code || botData.generated_code)
    setBacktestResults(botData.backtest_results)
    setInsightsConfig(botData.insights_config)
    setCurrentBotId(botData.id)
    setShowBotLibrary(false)
    setShowLanding(false)
    console.log('Loaded bot:', botData.name)
  }

  const handleRefineStrategy = async (refinementPrompt) => {
    // Close the sidebar
    setSidebarOpen(false)

    // Set refinement status to show loading overlay
    setRefinementStatus('refining')
    setLoading(true)
    setError(null)

    // Generate new session ID
    const newSessionId = crypto.randomUUID()
    setSessionId(newSessionId)

    try {
      console.log('[Refinement] 🔧 Starting intelligent refinement...')
      console.log('[Refinement] 📝 Request:', refinementPrompt)

      // Call the enhanced refine endpoint with iterative improvement
      const response = await fetch('http://localhost:8000/api/strategy/refine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_strategy: strategy,
          current_code: generatedCode,
          current_backtest_results: backtestResults,
          refinement_instructions: refinementPrompt,
          session_id: newSessionId
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to refine strategy')
      }

      const data = await response.json()

      // Update state with refined strategy - include final_analysis
      const updatedStrategy = {
        ...data.strategy,
        final_analysis: data.final_analysis
      }
      setStrategy(updatedStrategy)
      setGeneratedCode(data.code)
      setBacktestResults(data.backtest_results)
      setInsightsConfig(data.insights_config)

      // Log refinement results
      console.log('✅ Strategy refined successfully!')
      console.log(`📊 Iterations performed: ${data.iterations_performed}`)
      console.log(`🎯 Best performance score: ${data.best_score?.toFixed(2)}`)
      console.log(`🔧 Changes made:`, data.changes_made)

      if (data.iteration_history && data.iteration_history.length > 0) {
        console.log('📈 Iteration history:')
        data.iteration_history.forEach(hist => {
          console.log(`  Iteration ${hist.iteration}: Return ${hist.total_return?.toFixed(1)}%, Win Rate ${hist.win_rate?.toFixed(1)}%, Trades ${hist.total_trades}`)
        })
      }

      // Show success notification
      setRefinementStatus('success')

      // Hide success notification after 3 seconds
      setTimeout(() => {
        setRefinementStatus(null)
      }, 3000)

      setLoading(false)

      // Auto-save after refinement
      setTimeout(() => handleSaveBot(true), 1000)
    } catch (err) {
      console.error('❌ Error during refinement:', err)
      setError(err.message || 'Refinement failed')
      setRefinementStatus('error')
      setLoading(false)

      // Hide error notification after 5 seconds
      setTimeout(() => {
        setRefinementStatus(null)
      }, 5000)
    }
  }

  const handleGetStarted = () => {
    setShowLanding(false)
  }

  // Show landing page if user hasn't started
  if (showLanding && !generatedCode && !loading) {
    return (
      <div className="min-h-screen bg-dark-bg">
        <LandingPage
          onGetStarted={handleGetStarted}
          onShowSignup={() => setShowSignup(true)}
          user={user}
          onSignOut={handleSignOut}
          onShowBotLibrary={() => setShowBotLibrary(true)}
        />

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
            onSuccess={() => {
              setShowLogin(false)
              setShowLanding(false)
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
            onSuccess={() => {
              setShowSignup(false)
              setShowLanding(false)
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
            user={user}
            onSignOut={handleSignOut}
            onShowBotLibrary={() => setShowBotLibrary(true)}
          />
        )}
      </div>
    )
  }

  const handleNewChat = () => {
    setStrategy(null)
    setGeneratedCode(null)
    setBacktestResults(null)
    setInsightsConfig(null)
    setCurrentBotId(null)
    setError(null)
    setSessionId(null)
  }

  return (
    <div className="min-h-screen bg-dark-bg flex">
      {/* Chat History Sidebar */}
      {isAuthenticated && (
        <ChatHistorySidebar
          onNewChat={handleNewChat}
          onLoadBot={handleLoadBot}
          currentBotId={currentBotId}
        />
      )}

      {/* Main Content Container */}
      <div className="flex-1 flex flex-col">
        {/* Session Expired Modal */}
        <SessionExpiredModal
          isOpen={tokenExpiredError}
          onClose={() => {
            clearExpiredError()
            setShowLogin(true)
          }}
        />

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8 flex-1">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-6">
          {/* Left: Logo */}
          <button
            onClick={() => setShowLanding(true)}
            className="text-white hover:opacity-80 transition-opacity"
          >
            <span className="text-2xl font-serif italic">Mobius</span>
          </button>

          {/* Right: Action Buttons & Auth */}
          <div className="flex items-center gap-3">
            {/* Dashboard & Community buttons */}
            <button
              onClick={handleGetStarted}
              className="px-4 py-2 text-sm font-light rounded-lg border border-white/20 transition-colors text-white/80 hover:border-accent hover:text-accent"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/community')}
              className={`px-4 py-2 text-sm font-light rounded-lg border border-white/20 transition-colors ${
                location.pathname === '/community'
                  ? 'border-accent text-accent'
                  : 'text-white/80 hover:border-accent hover:text-accent'
              }`}
            >
              Community
            </button>
            <button
              onClick={() => setShowDeploymentMonitor(true)}
              className={`px-4 py-2 text-sm font-light rounded-lg border border-white/20 transition-colors ${
                showDeploymentMonitor
                  ? 'border-accent text-accent'
                  : 'text-white/80 hover:border-accent hover:text-accent'
              }`}
            >
              Deployments
            </button>

            {isAuthenticated ? (
              <>
                {generatedCode && backtestResults && (
                  <button
                    onClick={handleSaveBot}
                    className="px-4 py-2 text-sm font-light rounded-lg border border-white/20 bg-transparent transition-colors text-white/80 hover:border-accent hover:text-accent hover:bg-white/5"
                  >
                    Save Bot
                  </button>
                )}
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
                    <div className="absolute right-0 top-full mt-1 w-32 bg-dark-surface border border-dark-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                      <div className="py-1">
                        <button
                          onClick={() => setShowBotLibrary(true)}
                          className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-dark-bg hover:text-white transition-colors"
                        >
                          My Bots
                        </button>
                        <button
                          onClick={handleSignOut}
                          className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-dark-bg hover:text-red-300 transition-colors"
                        >
                          Sign Out
                        </button>
                      </div>
                    </div>
                  </div>
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
              </>
            )}
          </div>
        </div>
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Refinement Status Notification */}
        {refinementStatus === 'refining' && (
          <div className="fixed top-20 right-6 z-50 max-w-md animate-fade-in-up">
            <div className="bg-accent/20 border border-accent/50 rounded-lg p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <div className="w-5 h-5 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium text-sm">Refining Strategy...</p>
                  <p className="text-white/70 text-xs mt-1">
                    Running intelligent iterations with data analysis
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {refinementStatus === 'success' && (
          <div className="fixed top-20 right-6 z-50 max-w-md animate-fade-in-up">
            <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium text-sm">Strategy Refined Successfully!</p>
                  <p className="text-white/70 text-xs mt-1">
                    Check the console for detailed iteration results
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {refinementStatus === 'error' && (
          <div className="fixed top-20 right-6 z-50 max-w-md animate-fade-in-up">
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium text-sm">Refinement Failed</p>
                  <p className="text-white/70 text-xs mt-1">
                    {error || 'Please try again'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex-1 flex items-center justify-center min-h-screen">
            <div className="flex flex-col items-center text-center max-w-2xl w-full px-6">
              <div className="mb-6 flex flex-col items-center">
                <LoadingSpinner />
                <p className="text-gray-400 mt-4 text-lg font-semibold">
                  Multi-Agent System Working...
                </p>
                <p className="text-gray-500 text-sm mt-2">
                  Iterating through code generation, backtesting, and analysis
                </p>
              </div>

              {/* Real-time Agent Activity Log (WebSocket-based) */}
              {sessionId ? (
                <div className="mt-6 w-full max-w-3xl">
                  <AgentActivityLogWS
                    sessionId={sessionId}
                    onComplete={handleWorkflowComplete}
                  />
                </div>
              ) : (
                /* Fallback animated indicator if no session ID */
                <div className="flex justify-center w-full">
                  <ProgressIndicator />
                </div>
              )}
            </div>
          </div>
        ) : showDeploymentMonitor ? (
          <DeploymentMonitor
            onBack={() => setShowDeploymentMonitor(false)}
          />
        ) : showDeploymentPage ? (
          <DeploymentPage
            strategy={strategy}
            generatedCode={generatedCode}
            backtestResults={backtestResults}
            currentBotId={currentBotId}
            onBackToDashboard={() => setShowDeploymentPage(false)}
            onViewDeployments={() => {
              setShowDeploymentPage(false)
              setShowDeploymentMonitor(true)
            }}
          />
        ) : !generatedCode ? (
          <div className="max-w-7xl mx-auto px-6 py-8 w-full">
            <StrategyInput onGenerate={handleGenerateStrategy} fastMode={fastMode} onFastModeChange={setFastMode} />
          </div>
        ) : (
          <div className="flex flex-1 gap-0 overflow-hidden w-full">
            {/* Main Content */}
            <div className={`flex-1 overflow-y-auto px-12 py-8 transition-all duration-300 ${
              sidebarOpen ? 'mr-[380px] md:mr-[420px]' : 'mr-0'
            }`}>
            {error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
                <p className="font-medium">Error</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            )}

            <div className="space-y-6">
            {/* Strategy Summary */}
            {strategy && (
              <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-5">
                <div className="mb-4">
                  <h2 className="text-sm font-light text-white">Strategy Overview</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-white/50">Asset</p>
                    <p className="mt-1 text-base font-semibold text-white">{strategy.asset}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/50">Take Profit</p>
                    <p className="mt-1 text-base font-semibold text-green-400">
                      +{(strategy.exit_conditions?.take_profit * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-white/50">Stop Loss</p>
                    <p className="mt-1 text-base font-semibold text-red-400">
                      -{(strategy.exit_conditions?.stop_loss * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-white/10">
                  <p className="text-xs text-white/50 mb-2">Data Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {strategy.data_sources?.map((source) => (
                      <span
                        key={source}
                        className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-white/50"
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
              <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-5">
                <div className="mb-4">
                  <h2 className="text-sm font-light text-white">Backtest Results</h2>
                </div>
                <BacktestResults results={backtestResults} insightsConfig={insightsConfig} />
              </div>
            )}

            {/* Generated Code */}
            <CodeDisplay code={generatedCode} strategyName={strategy?.name} />

            {/* Deploy Button */}
            {backtestResults && (
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowDeploymentPage(true)}
                  className="px-8 py-3 rounded-lg bg-accent text-white font-medium hover:bg-accent/90 transition-colors flex items-center gap-2"
                >
                  Proceed to Deployment
                  <span>→</span>
                </button>
              </div>
            )}
            </div>
            </div>

            {/* Refine Sidebar - fixed right-side panel with vertical handle */}
            {strategy && (
              <RefineSidebar
                currentStrategy={strategy}
                onRefineStrategy={handleRefineStrategy}
                onRunBacktest={handleRunBacktest}
                onOpenChange={setSidebarOpen}
              />
            )}
          </div>
        )}
      </main>

      </div>
      {/* End Main Content Container */}

      {/* Auth Modals */}
      {showLogin && (
        <Login
          onClose={() => setShowLogin(false)}
          onSwitchToSignup={() => {
            setShowLogin(false)
            setShowSignup(true)
          }}
          onSuccess={() => {
            setShowLogin(false)
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
          onSuccess={() => {
            setShowSignup(false)
          }}
        />
      )}

      {/* Bot Library Modal */}
      {showBotLibrary && (
        <BotLibrary
          onClose={() => setShowBotLibrary(false)}
          onLoadBot={handleLoadBot}
          user={user}
          onSignOut={handleSignOut}
          onShowBotLibrary={() => setShowBotLibrary(true)}
        />
      )}

    </div>
  )
}

function App() {
  return <AppContent />
}

export default App
