import { API_URL } from '../config'
import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

const DeploymentMonitor = ({ onBack }) => {
  const { getAuthHeaders, isAuthenticated } = useAuth()
  const [deployments, setDeployments] = useState([])
  const [selectedDeployment, setSelectedDeployment] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [trades, setTrades] = useState([])
  const [positions, setPositions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch all deployments
  const fetchDeployments = async () => {
    if (!isAuthenticated) return

    try {
      const response = await fetch(`${API_URL}/deployments`, {
        headers: getAuthHeaders()
      })

      if (!response.ok) throw new Error('Failed to fetch deployments')

      const data = await response.json()
      setDeployments(data)

      // Auto-select first deployment if exists
      if (data.length > 0 && !selectedDeployment) {
        setSelectedDeployment(data[0])
      }
    } catch (err) {
      console.error('Error fetching deployments:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Fetch deployment details
  const fetchDeploymentDetails = async (deploymentId) => {
    if (!isAuthenticated) return

    try {
      const [metricsRes, tradesRes, positionsRes] = await Promise.all([
        fetch(`http://localhost:8000/deployments/${deploymentId}/metrics?limit=100`, {
          headers: getAuthHeaders()
        }),
        fetch(`http://localhost:8000/deployments/${deploymentId}/trades?limit=50`, {
          headers: getAuthHeaders()
        }),
        fetch(`http://localhost:8000/deployments/${deploymentId}/positions`, {
          headers: getAuthHeaders()
        })
      ])

      if (metricsRes.ok) setMetrics(await metricsRes.json())
      if (tradesRes.ok) setTrades(await tradesRes.json())
      if (positionsRes.ok) setPositions(await positionsRes.json())
    } catch (err) {
      console.error('Error fetching deployment details:', err)
    }
  }

  // Handle deployment status change
  const handleStatusChange = async (deploymentId, action) => {
    try {
      const response = await fetch(`http://localhost:8000/deployments/${deploymentId}/${action}`, {
        method: 'POST',
        headers: getAuthHeaders()
      })

      if (!response.ok) throw new Error(`Failed to ${action} deployment`)

      // Refresh deployments
      fetchDeployments()
      alert(`Deployment ${action}d successfully`)
    } catch (err) {
      console.error(`Error ${action}ing deployment:`, err)
      alert(`Failed to ${action} deployment: ${err.message}`)
    }
  }

  useEffect(() => {
    fetchDeployments()
    const interval = setInterval(fetchDeployments, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [isAuthenticated])

  useEffect(() => {
    if (selectedDeployment) {
      fetchDeploymentDetails(selectedDeployment.id)
      const interval = setInterval(() => fetchDeploymentDetails(selectedDeployment.id), 5000)
      return () => clearInterval(interval)
    }
  }, [selectedDeployment])

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'text-green-400 bg-green-400/10 border-green-400/20'
      case 'paused': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      case 'stopped': return 'text-red-400 bg-red-400/10 border-red-400/20'
      case 'error': return 'text-red-400 bg-red-400/10 border-red-400/20'
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-white">Loading deployments...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-white">Please sign in to view deployments</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold text-white mb-2">Live Deployments</h1>
            <p className="text-gray-400">Monitor your paper trading strategies</p>
          </div>
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-lg border border-white/20 text-white/80 hover:border-accent hover:text-accent transition-colors"
          >
            ← Back to Dashboard
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {deployments.length === 0 ? (
          <div className="text-center py-16">
            <h2 className="text-xl text-white mb-2">No Active Deployments</h2>
            <p className="text-gray-400 mb-6">Deploy a strategy to start live paper trading</p>
            <button
              onClick={onBack}
              className="px-6 py-3 rounded-lg bg-accent text-white hover:bg-accent/90 transition-colors"
            >
              Go to Backtesting
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-12 gap-6">
            {/* Deployments List */}
            <div className="col-span-4 space-y-4">
              <h3 className="text-sm font-light text-white/70 mb-4">Your Deployments ({deployments.length})</h3>
              {deployments.map((deployment) => (
                <div
                  key={deployment.id}
                  onClick={() => setSelectedDeployment(deployment)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedDeployment?.id === deployment.id
                      ? 'border-accent bg-accent/5'
                      : 'border-white/10 bg-[#0e1117] hover:border-white/20'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className={`inline-block px-2 py-1 rounded text-xs font-medium border mb-2 ${getStatusColor(deployment.status)}`}>
                        {deployment.status.toUpperCase()}
                      </div>
                      <p className="text-sm text-white/50">Bot ID: {deployment.bot_id.slice(0, 8)}...</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs text-white/40">Total P&L</p>
                      <p className={`text-base font-medium ${deployment.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ${deployment.total_pnl?.toFixed(2) || '0.00'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-white/40">Return</p>
                      <p className={`text-base font-medium ${deployment.total_return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {deployment.total_return_pct?.toFixed(2) || '0.00'}%
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-white/40">
                      Started: {new Date(deployment.deployed_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Deployment Details */}
            <div className="col-span-8">
              {selectedDeployment ? (
                <div className="space-y-6">
                  {/* Overview Cards */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                      <p className="text-xs text-white/50 mb-1">Portfolio Value</p>
                      <p className="text-xl font-semibold text-white">
                        ${selectedDeployment.current_capital?.toFixed(2) || selectedDeployment.initial_capital.toFixed(2)}
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                      <p className="text-xs text-white/50 mb-1">Total P&L</p>
                      <p className={`text-xl font-semibold ${selectedDeployment.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ${selectedDeployment.total_pnl?.toFixed(2) || '0.00'}
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                      <p className="text-xs text-white/50 mb-1">Return</p>
                      <p className={`text-xl font-semibold ${selectedDeployment.total_return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {selectedDeployment.total_return_pct?.toFixed(2) || '0.00'}%
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                      <p className="text-xs text-white/50 mb-1">Frequency</p>
                      <p className="text-xl font-semibold text-white">{selectedDeployment.execution_frequency}</p>
                    </div>
                  </div>

                  {/* Controls */}
                  <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                    <h3 className="text-sm font-light text-white mb-4">Controls</h3>
                    <div className="flex gap-3">
                      {selectedDeployment.status === 'running' && (
                        <button
                          onClick={() => handleStatusChange(selectedDeployment.id, 'pause')}
                          className="px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/30 transition-colors"
                        >
                          Pause
                        </button>
                      )}
                      {selectedDeployment.status === 'paused' && (
                        <button
                          onClick={() => handleStatusChange(selectedDeployment.id, 'resume')}
                          className="px-4 py-2 rounded-lg bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30 transition-colors"
                        >
                          Resume
                        </button>
                      )}
                      {selectedDeployment.status !== 'stopped' && (
                        <button
                          onClick={() => {
                            if (confirm('Are you sure you want to stop this deployment?')) {
                              handleStatusChange(selectedDeployment.id, 'stop')
                            }
                          }}
                          className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-colors"
                        >
                          Stop
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Open Positions */}
                  <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                    <h3 className="text-sm font-light text-white mb-4">Open Positions ({positions.length})</h3>
                    {positions.length === 0 ? (
                      <p className="text-sm text-white/40">No open positions</p>
                    ) : (
                      <div className="space-y-3">
                        {positions.map((position) => (
                          <div key={position.id} className="p-3 rounded bg-white/5 border border-white/10">
                            <div className="flex justify-between items-start">
                              <div>
                                <p className="font-medium text-white">{position.symbol}</p>
                                <p className="text-sm text-white/50">{position.quantity} shares @ ${position.entry_price?.toFixed(2)}</p>
                              </div>
                              <div className="text-right">
                                <p className={`font-medium ${position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  ${position.unrealized_pnl?.toFixed(2) || '0.00'}
                                </p>
                                <p className={`text-sm ${position.unrealized_pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  {position.unrealized_pnl_pct?.toFixed(2) || '0.00'}%
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Recent Trades */}
                  <div className="p-4 rounded-lg border border-white/10 bg-[#0e1117]">
                    <h3 className="text-sm font-light text-white mb-4">Recent Trades ({trades.length})</h3>
                    {trades.length === 0 ? (
                      <p className="text-sm text-white/40">No trades yet</p>
                    ) : (
                      <div className="space-y-2">
                        {trades.slice(0, 10).map((trade) => (
                          <div key={trade.id} className="p-3 rounded bg-white/5 border border-white/10 flex justify-between items-center">
                            <div>
                              <span className={`inline-block px-2 py-1 rounded text-xs ${
                                trade.side === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                              }`}>
                                {trade.side.toUpperCase()}
                              </span>
                              <span className="ml-2 text-white">{trade.symbol}</span>
                              <span className="ml-2 text-white/50 text-sm">{trade.quantity} @ ${trade.price?.toFixed(2)}</span>
                            </div>
                            <div className="text-right">
                              <p className="text-sm text-white/50">{new Date(trade.executed_at).toLocaleString()}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-16 text-white/50">
                  Select a deployment to view details
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default DeploymentMonitor
