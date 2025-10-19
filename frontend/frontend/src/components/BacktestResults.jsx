import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import AdditionalInfoCharts from './AdditionalInfoCharts'
import DynamicInsightsCharts from './DynamicInsightsCharts'

// Custom tooltip defined outside component to avoid React version issues
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-dark-surface border border-dark-border rounded-lg p-3 shadow-lg">
        <p className="text-white font-semibold mb-2">{payload[0].payload.date}</p>
        <p className="text-accent-primary text-sm font-semibold">
          Strategy: ${payload[0].value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
        {payload[1] && (
          <p className="text-accent-success text-sm font-semibold">
            Buy & Hold: ${payload[1].value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        )}
        <div className="border-t border-dark-border mt-2 pt-2">
          <p className="text-gray-400 text-xs">
            Cash: ${payload[0].payload.cash.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-gray-400 text-xs">
            Position: ${payload[0].payload.position_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>
    )
  }
  return null
}

export default function BacktestResults({ results, insightsConfig }) {
  const [showAllTrades, setShowAllTrades] = useState(false)

  if (!results) return null

  const { summary, trades, portfolio_history, additional_info } = results

  const getReturnColor = (value) => {
    if (value > 0) return 'text-accent-success'
    if (value < 0) return 'text-accent-danger'
    return 'text-gray-400'
  }

  const getReturnBgColor = (value) => {
    if (value > 0) return 'bg-accent-success/10 border-accent-success/30'
    if (value < 0) return 'bg-accent-danger/10 border-accent-danger/30'
    return 'bg-gray-500/10 border-gray-500/30'
  }

  const displayedTrades = showAllTrades ? trades : trades.slice(0, 5)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-3xl">📊</span>
          <div>
            <h2 className="text-3xl font-light text-fg">Backtest Results</h2>
            <p className="text-sm text-gray-400">
              {summary.symbol} • {summary.start_date} to {summary.end_date}
            </p>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Total Return</p>
            <p className={`text-3xl font-bold ${getReturnColor(summary.total_return)}`}>
              {summary.total_return > 0 ? '+' : ''}{summary.total_return}%
            </p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Buy & Hold</p>
            <p className={`text-3xl font-bold ${getReturnColor(summary.buy_hold_return)}`}>
              {summary.buy_hold_return > 0 ? '+' : ''}{summary.buy_hold_return}%
            </p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Win Rate</p>
            <p className="text-3xl font-bold text-white">
              {summary.win_rate}%
            </p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Total Trades</p>
            <p className="text-3xl font-bold text-white">
              {summary.total_trades}
            </p>
          </div>
        </div>

        {/* Performance Comparison Banner */}
        <div className={`p-4 rounded-lg border ${getReturnBgColor(summary.total_return - summary.buy_hold_return)}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Strategy vs Buy & Hold {summary.symbol}</p>
              <p className={`text-xl font-bold ${getReturnColor(summary.total_return - summary.buy_hold_return)}`}>
                {summary.total_return > summary.buy_hold_return ? '📈 Outperformed' : '📉 Underperformed'} {summary.symbol} by {Math.abs(summary.total_return - summary.buy_hold_return).toFixed(2)}%
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Final Capital</p>
              <p className="text-xl font-bold text-white">
                ${summary.final_capital.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className={`text-sm ${getReturnColor(summary.final_capital - summary.initial_capital)}`}>
                {summary.final_capital > summary.initial_capital ? '+' : ''}${(summary.final_capital - summary.initial_capital).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Performance Chart */}
      <div className="card">
        <h3 className="text-2xl font-light text-fg mb-4">📈 Portfolio Value Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={portfolio_history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getMonth() + 1}/${date.getDate()}`
              }}
            />
            <YAxis
              stroke="#6b7280"
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: '#9ca3af' }} />
            <Line
              type="monotone"
              dataKey="portfolio_value"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="Strategy"
            />
            <Line
              type="monotone"
              dataKey="buy_hold_value"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
              name={`Buy & Hold ${summary.symbol}`}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Additional Info Charts (Indicators/Sentiment) - Dynamic or Legacy */}
      {additional_info && additional_info.length > 0 && (
        insightsConfig ? (
          <DynamicInsightsCharts additionalInfo={additional_info} insightsConfig={insightsConfig} />
        ) : (
          <AdditionalInfoCharts additionalInfo={additional_info} />
        )
      )}

      {/* Detailed Metrics */}
      <div className="card">
        <h3 className="text-2xl font-light text-fg mb-4">📋 Detailed Metrics</h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Winning Trades</p>
            <p className="text-lg font-semibold text-accent-success">
              {summary.winning_trades} ({((summary.winning_trades / summary.total_trades) * 100).toFixed(0)}%)
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Losing Trades</p>
            <p className="text-lg font-semibold text-accent-danger">
              {summary.losing_trades} ({((summary.losing_trades / summary.total_trades) * 100).toFixed(0)}%)
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Avg Win</p>
            <p className="text-lg font-semibold text-accent-success">
              ${summary.avg_win.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Avg Loss</p>
            <p className="text-lg font-semibold text-accent-danger">
              ${summary.avg_loss.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Max Win</p>
            <p className="text-lg font-semibold text-accent-success">
              ${summary.max_win.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Max Loss</p>
            <p className="text-lg font-semibold text-accent-danger">
              ${summary.max_loss.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Avg Days Held</p>
            <p className="text-lg font-semibold text-white">
              {summary.avg_days_held} days
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Max Drawdown</p>
            <p className="text-lg font-semibold text-accent-danger">
              -{summary.max_drawdown.toFixed(2)}%
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
            <p className="text-lg font-semibold text-white">
              {summary.sharpe_ratio.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Profit Factor</p>
            <p className={`text-lg font-semibold ${summary.profit_factor >= 1 ? 'text-accent-success' : 'text-accent-danger'}`}>
              {summary.profit_factor.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Trade History */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-light text-fg">📝 Trade History</h3>
          {trades.length > 5 && (
            <button
              onClick={() => setShowAllTrades(!showAllTrades)}
              className="text-sm text-accent-primary hover:text-blue-400 transition-colors"
            >
              {showAllTrades ? 'Show Less' : `Show All ${trades.length} Trades`}
            </button>
          )}
        </div>

        <div className="space-y-3">
          {displayedTrades.map((trade) => (
            <div
              key={trade.trade_number}
              className={`p-4 rounded-lg border ${
                trade.pnl > 0
                  ? 'bg-accent-success/5 border-accent-success/20'
                  : 'bg-accent-danger/5 border-accent-danger/20'
              }`}
            >
              {/* Trade Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {trade.pnl > 0 ? '✅' : '❌'}
                  </span>
                  <div>
                    <p className="text-white font-semibold">
                      Trade #{trade.trade_number} • {trade.symbol}
                    </p>
                    <p className="text-xs text-gray-400">
                      {trade.days_held} day{trade.days_held !== 1 ? 's' : ''} held
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-xl font-bold ${getReturnColor(trade.pnl)}`}>
                    {trade.pnl > 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </p>
                  <p className={`text-sm ${getReturnColor(trade.pnl_pct)}`}>
                    {trade.pnl_pct > 0 ? '+' : ''}{trade.pnl_pct.toFixed(2)}%
                  </p>
                </div>
              </div>

              {/* Trade Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                {/* Entry */}
                <div className="bg-dark-bg p-3 rounded-lg">
                  <p className="text-xs text-gray-400 mb-2">📥 ENTRY</p>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Date:</span>
                      <span className="text-sm text-white">{trade.entry_date}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Price:</span>
                      <span className="text-sm text-white">${trade.entry_price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Shares:</span>
                      <span className="text-sm text-white">{trade.shares}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Value:</span>
                      <span className="text-sm text-white">
                        ${(trade.entry_price * trade.shares).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Exit */}
                <div className="bg-dark-bg p-3 rounded-lg">
                  <p className="text-xs text-gray-400 mb-2">📤 EXIT</p>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Date:</span>
                      <span className="text-sm text-white">{trade.exit_date}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Price:</span>
                      <span className="text-sm text-white">${trade.exit_price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Shares:</span>
                      <span className="text-sm text-white">{trade.shares}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-400">Value:</span>
                      <span className="text-sm text-white">
                        ${(trade.exit_price * trade.shares).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Trade Reasoning */}
              <div className="border-t border-dark-border pt-3 space-y-2">
                <div className="flex items-start gap-2">
                  <span className="text-gray-400 text-sm">📍</span>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400">Entry Reason:</p>
                    <p className="text-sm text-white">{trade.entry_reason}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-gray-400 text-sm">🎯</span>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400">Exit Reason:</p>
                    <p className="text-sm text-white capitalize">
                      {trade.exit_reason.replace('_', ' ')}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-gray-400 text-sm">💰</span>
                  <div className="flex-1">
                    <p className="text-xs text-gray-400">Capital Impact:</p>
                    <p className="text-sm text-white">
                      ${trade.capital_before.toLocaleString()} → ${trade.capital_after.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {!showAllTrades && trades.length > 5 && (
          <div className="mt-4 text-center">
            <button
              onClick={() => setShowAllTrades(true)}
              className="btn btn-secondary text-sm"
            >
              View {trades.length - 5} More Trades
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
