import { API_URL } from '../config'
import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DeploymentConfirmationModal from './DeploymentConfirmationModal'

const DeploymentPage = ({
  strategy,
  generatedCode,
  backtestResults,
  currentBotId,
  onBackToDashboard,
  onViewDeployments
}) => {
  const { getAuthHeaders, isAuthenticated } = useAuth()
  const [deploymentConfig, setDeploymentConfig] = useState({
    initialCapital: 10000,
    executionFrequency: '5min',
    maxPositionSize: 2000,
    dailyLossLimit: 500
  })
  const [deploying, setDeploying] = useState(false)
  const [deploymentId, setDeploymentId] = useState(null)
  const [error, setError] = useState(null)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [isPaperTrading, setIsPaperTrading] = useState(true)

  useEffect(() => {
    console.log('[DeploymentPage] currentBotId:', currentBotId)
  }, [currentBotId])

  const handleInitiateDeploy = () => {
    if (!isAuthenticated) {
      setError('Please sign in to deploy strategies')
      return
    }

    if (!currentBotId) {
      setError('No bot ID found. Please save the strategy first.')
      return
    }

    // Show confirmation modal
    setShowConfirmation(true)
  }

  const handleConfirmedDeploy = async () => {
    setShowConfirmation(false)
    setDeploying(true)
    setError(null)

    try {
      // Step 1: Create deployment
      console.log('Creating deployment for bot:', currentBotId)
      const createResponse = await fetch(`${API_URL}/deployments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({
          bot_id: currentBotId,
          initial_capital: deploymentConfig.initialCapital,
          execution_frequency: deploymentConfig.executionFrequency,
          max_position_size: deploymentConfig.maxPositionSize,
          daily_loss_limit: deploymentConfig.dailyLossLimit,
          paper_trading: isPaperTrading
        })
      })

      if (!createResponse.ok) {
        const errorData = await createResponse.json()
        throw new Error(errorData.detail || 'Failed to deploy strategy')
      }

      const deployment = await createResponse.json()
      console.log('✅ Deployment created:', deployment)

      // Step 2: Activate deployment (start live trading)
      console.log('Activating deployment:', deployment.id)
      const activateResponse = await fetch(`${API_URL}/deployments/${deployment.id}/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      })

      if (!activateResponse.ok) {
        const errorData = await activateResponse.json()
        throw new Error(errorData.detail || 'Failed to activate deployment')
      }

      const activationResult = await activateResponse.json()
      console.log('✅ Deployment activated:', activationResult)

      setDeploymentId(deployment.id)

    } catch (err) {
      console.error('Deployment error:', err)
      setError(err.message)
    } finally {
      setDeploying(false)
    }
  }

  if (deploymentId) {
    return (
      <div className="min-h-screen bg-dark-bg">
        <main className="max-w-7xl mx-auto px-6 py-8">
          <button
            onClick={onBackToDashboard}
            className="mb-6 px-4 py-2 text-sm rounded-lg border border-white/20 text-white/80 hover:border-accent hover:text-accent transition-colors"
          >
            ← Back to Dashboard
          </button>
          {/* Success Message */}
          <div className="rounded-2xl border border-green-500/20 bg-green-500/10 p-8 text-center">
            <h2 className="text-2xl font-semibold text-white mb-2">
              Strategy Deployed Successfully!
            </h2>
            <p className="text-gray-400 mb-6">
              Your trading bot is now live on Alpaca paper trading
            </p>

            <div className="inline-block rounded-lg border border-white/10 bg-white/5 px-6 py-3 mb-6">
              <p className="text-xs text-white/50 mb-1">Deployment ID</p>
              <p className="text-sm font-mono text-white">{deploymentId}</p>
            </div>

            <div className="flex gap-3 justify-center">
              <button
                onClick={onBackToDashboard}
                className="px-6 py-3 rounded-lg border border-white/20 text-white hover:border-accent hover:text-accent transition-colors"
              >
                Back to Dashboard
              </button>
              <button
                onClick={onViewDeployments}
                className="px-6 py-3 rounded-lg bg-accent text-white hover:bg-accent/90 transition-colors"
              >
                View Deployments →
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Confirmation Modal */}
        <DeploymentConfirmationModal
          isOpen={showConfirmation}
          onClose={() => setShowConfirmation(false)}
          onConfirm={handleConfirmedDeploy}
          deploymentConfig={deploymentConfig}
          strategy={strategy}
          backtestResults={backtestResults}
          isPaperTrading={isPaperTrading}
        />

        <button
          onClick={onBackToDashboard}
          className="mb-6 px-4 py-2 text-sm rounded-lg border border-white/20 text-white/80 hover:border-accent hover:text-accent transition-colors"
        >
          ← Back to Backtesting
        </button>
        <div className="mb-8">
          <h2 className="text-3xl font-semibold text-white mb-2">
            Deploy to {isPaperTrading ? 'Paper' : 'Live'} Trading
          </h2>
          <p className="text-gray-400">
            Configure your deployment settings and go live with Alpaca
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
            <p className="font-medium">Deployment Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Strategy Summary */}
        <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-6 mb-6">
          <h3 className="text-sm font-light text-white mb-4">Strategy Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-white/50">Asset</p>
              <p className="text-base text-white mt-1">{strategy?.asset || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-white/50">Strategy Type</p>
              <p className="text-base text-white mt-1">{strategy?.strategy_type || 'N/A'}</p>
            </div>
            {backtestResults && (
              <>
                <div>
                  <p className="text-xs text-white/50">Backtest Return</p>
                  <p className="text-base text-green-400 mt-1">
                    +{backtestResults.total_return?.toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-white/50">Win Rate</p>
                  <p className="text-base text-white mt-1">
                    {(backtestResults.win_rate * 100).toFixed(1)}%
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Trading Mode Toggle */}
        <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-6 mb-6">
          <h3 className="text-sm font-light text-white mb-4">Trading Mode</h3>
          <div className="flex gap-4">
            <button
              onClick={() => setIsPaperTrading(true)}
              className={`flex-1 py-3 rounded-lg border-2 transition-all ${
                isPaperTrading
                  ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                  : 'border-white/10 text-white/50 hover:border-white/20'
              }`}
            >
              <div className="text-sm font-medium">Paper Trading</div>
              <div className="text-xs mt-1">Simulated funds - No real risk</div>
            </button>
            <button
              onClick={() => setIsPaperTrading(false)}
              className={`flex-1 py-3 rounded-lg border-2 transition-all ${
                !isPaperTrading
                  ? 'border-red-500 bg-red-500/10 text-red-400'
                  : 'border-white/10 text-white/50 hover:border-white/20'
              }`}
            >
              <div className="text-sm font-medium">Live Trading</div>
              <div className="text-xs mt-1">Real money - Actual risk</div>
            </button>
          </div>
        </div>

        {/* Deployment Configuration */}
        <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-6 mb-6">
          <h3 className="text-sm font-light text-white mb-6">Deployment Configuration</h3>

          <div className="space-y-6">
            {/* Initial Capital */}
            <div>
              <label className="block text-sm text-white/70 mb-2">
                Initial Capital
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/50">$</span>
                <input
                  type="number"
                  value={deploymentConfig.initialCapital}
                  onChange={(e) => setDeploymentConfig({
                    ...deploymentConfig,
                    initialCapital: parseFloat(e.target.value)
                  })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-10 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                  min="100"
                  step="100"
                />
              </div>
              <p className="text-xs text-white/40 mt-1">
                Amount to allocate for this strategy (paper trading funds)
              </p>
            </div>

            {/* Execution Frequency */}
            <div>
              <label className="block text-sm text-white/70 mb-2">
                Execution Frequency
              </label>
              <select
                value={deploymentConfig.executionFrequency}
                onChange={(e) => setDeploymentConfig({
                  ...deploymentConfig,
                  executionFrequency: e.target.value
                })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-accent transition-colors"
              >
                <option value="1min">Every 1 minute</option>
                <option value="5min">Every 5 minutes</option>
                <option value="15min">Every 15 minutes</option>
                <option value="30min">Every 30 minutes</option>
                <option value="1hour">Every 1 hour</option>
              </select>
              <p className="text-xs text-white/40 mt-1">
                How often the strategy should check for signals
              </p>
            </div>

            {/* Max Position Size */}
            <div>
              <label className="block text-sm text-white/70 mb-2">
                Max Position Size (Optional)
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/50">$</span>
                <input
                  type="number"
                  value={deploymentConfig.maxPositionSize}
                  onChange={(e) => setDeploymentConfig({
                    ...deploymentConfig,
                    maxPositionSize: parseFloat(e.target.value) || null
                  })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-10 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                  min="0"
                  step="100"
                />
              </div>
              <p className="text-xs text-white/40 mt-1">
                Maximum dollar amount per position
              </p>
            </div>

            {/* Daily Loss Limit */}
            <div>
              <label className="block text-sm text-white/70 mb-2">
                Daily Loss Limit (Optional)
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/50">$</span>
                <input
                  type="number"
                  value={deploymentConfig.dailyLossLimit}
                  onChange={(e) => setDeploymentConfig({
                    ...deploymentConfig,
                    dailyLossLimit: parseFloat(e.target.value) || null
                  })}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-10 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                  min="0"
                  step="50"
                />
              </div>
              <p className="text-xs text-white/40 mt-1">
                Auto-stop trading if daily loss exceeds this amount
              </p>
            </div>
          </div>
        </div>

        {/* Warning Box */}
        {isPaperTrading ? (
          <div className="rounded-lg border border-blue-500/20 bg-blue-500/10 p-4 mb-6">
            <div className="flex gap-3">
              <div className="text-blue-500 text-xl">ℹ</div>
              <div>
                <p className="text-sm text-blue-500 font-medium mb-1">Paper Trading Mode</p>
                <p className="text-xs text-blue-500/80">
                  This deployment uses Alpaca's paper trading environment with simulated funds.
                  No real money is at risk. Perfect for testing your strategy.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 mb-6">
            <div className="flex gap-3">
              <div className="text-red-500 text-xl">⚠</div>
              <div>
                <p className="text-sm text-red-500 font-medium mb-1">Live Trading Mode</p>
                <p className="text-xs text-red-500/80">
                  This deployment will execute REAL trades with REAL MONEY. All trades are final and
                  cannot be undone. Please ensure you have thoroughly tested in paper trading first.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Deploy Button */}
        <button
          onClick={handleInitiateDeploy}
          disabled={deploying || !isAuthenticated}
          className={`w-full py-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
            isPaperTrading
              ? 'bg-blue-500 hover:bg-blue-600 text-white'
              : 'bg-red-500 hover:bg-red-600 text-white'
          }`}
        >
          {deploying ? 'Deploying...' : `Deploy to ${isPaperTrading ? 'Paper' : 'Live'} Trading`}
        </button>

        {!isAuthenticated && (
          <p className="text-center text-sm text-red-400 mt-4">
            Please sign in to deploy strategies
          </p>
        )}
      </main>
    </div>
  )
}

export default DeploymentPage
