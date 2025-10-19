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
          <p className="text-white text-sm font-semibold">
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
    <div className="space-y-4">
      {/* Header */}
      <div>
        <p className="text-xs text-white/50 mb-2">
          {summary.symbol} • {summary.start_date} to {summary.end_date}
        </p>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Total Return</p>
            <p className={`text-2xl font-semibold ${getReturnColor(summary.total_return)}`}>
              {summary.total_return > 0 ? '+' : ''}{summary.total_return}%
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Buy & Hold</p>
            <p className={`text-2xl font-semibold ${getReturnColor(summary.buy_hold_return)}`}>
              {summary.buy_hold_return > 0 ? '+' : ''}{summary.buy_hold_return}%
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Win Rate</p>
            <p className="text-2xl font-semibold text-white">
              {summary.win_rate}%
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Total Trades</p>
            <p className="text-2xl font-semibold text-white">
              {summary.total_trades}
            </p>
          </div>
        </div>

        {/* Performance Comparison Banner */}
        <div className={`p-3 rounded-lg border ${getReturnBgColor(summary.total_return - summary.buy_hold_return)}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-white/50">Strategy vs Buy & Hold {summary.symbol}</p>
              <p className={`text-base font-semibold ${getReturnColor(summary.total_return - summary.buy_hold_return)}`}>
                {summary.total_return > summary.buy_hold_return ? 'Outperformed' : 'Underperformed'} by {Math.abs(summary.total_return - summary.buy_hold_return).toFixed(2)}%
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-white/50">Final Capital</p>
              <p className="text-base font-semibold text-white">
                ${summary.final_capital.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className={`text-xs ${getReturnColor(summary.final_capital - summary.initial_capital)}`}>
                {summary.final_capital > summary.initial_capital ? '+' : ''}${(summary.final_capital - summary.initial_capital).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Performance Chart */}
      <div className="mt-2 pt-2 border-t border-white/10">
        <h3 className="text-sm font-light text-white mb-2">Portfolio Value Over Time</h3>
        <ResponsiveContainer width="100%" height={600}>
          <LineChart data={portfolio_history} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
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
              stroke="#7c3aed"
              strokeWidth={2}
              dot={false}
              name="Strategy"
            />
            <Line
              type="monotone"
              dataKey="buy_hold_value"
              stroke="#ffffff"
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
      <div className="mt-4 pt-4 border-t border-white/10">
        <h3 className="text-sm font-light text-white mb-3">Detailed Metrics</h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Winning Trades</p>
            <p className="text-base font-semibold text-green-400">
              {summary.winning_trades} ({((summary.winning_trades / summary.total_trades) * 100).toFixed(0)}%)
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Losing Trades</p>
            <p className="text-base font-semibold text-red-400">
              {summary.losing_trades} ({((summary.losing_trades / summary.total_trades) * 100).toFixed(0)}%)
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Avg Win</p>
            <p className="text-base font-semibold text-green-400">
              ${summary.avg_win.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Avg Loss</p>
            <p className="text-base font-semibold text-red-400">
              ${summary.avg_loss.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Max Win</p>
            <p className="text-base font-semibold text-green-400">
              ${summary.max_win.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Max Loss</p>
            <p className="text-base font-semibold text-red-400">
              ${summary.max_loss.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Avg Days Held</p>
            <p className="text-base font-semibold text-white">
              {summary.avg_days_held} days
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Max Drawdown</p>
            <p className="text-base font-semibold text-red-400">
              -{summary.max_drawdown.toFixed(2)}%
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Sharpe Ratio</p>
            <p className="text-base font-semibold text-white">
              {summary.sharpe_ratio.toFixed(2)}
            </p>
          </div>

          <div className="p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-white/50 mb-1">Profit Factor</p>
            <p className={`text-base font-semibold ${summary.profit_factor >= 1 ? 'text-green-400' : 'text-red-400'}`}>
              {summary.profit_factor.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Trade History */}
      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-light text-white">Trade History</h3>
          {trades.length > 5 && (
            <button
              onClick={() => setShowAllTrades(!showAllTrades)}
              className="text-xs text-accent hover:text-accent/80 transition-colors"
            >
              {showAllTrades ? 'Show Less' : `Show All ${trades.length} Trades`}
            </button>
          )}
        </div>

        <div className="space-y-2">
          {displayedTrades.map((trade) => (
            <div
              key={trade.trade_number}
              className={`p-3 rounded-lg border ${
                trade.pnl > 0
                  ? 'bg-green-400/5 border-green-400/20'
                  : 'bg-red-400/5 border-red-400/20'
              }`}
            >
              {/* Trade Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div>
                    <p className="text-sm font-semibold text-white">
                      Trade #{trade.trade_number} • {trade.symbol}
                    </p>
                    <p className="text-xs text-white/50">
                      {trade.days_held} day{trade.days_held !== 1 ? 's' : ''} held
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-base font-semibold ${getReturnColor(trade.pnl)}`}>
                    {trade.pnl > 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </p>
                  <p className={`text-xs ${getReturnColor(trade.pnl_pct)}`}>
                    {trade.pnl_pct > 0 ? '+' : ''}{trade.pnl_pct.toFixed(2)}%
                  </p>
                </div>
              </div>

              {/* Trade Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
                {/* Entry */}
                <div className="bg-white/5 p-2 rounded-lg">
                  <p className="text-xs text-white/50 mb-1">ENTRY</p>
                  <div className="space-y-0.5">
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Date:</span>
                      <span className="text-xs text-white">{trade.entry_date}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Price:</span>
                      <span className="text-xs text-white">${trade.entry_price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Shares:</span>
                      <span className="text-xs text-white">{trade.shares}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Value:</span>
                      <span className="text-xs text-white">
                        ${(trade.entry_price * trade.shares).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Exit */}
                <div className="bg-white/5 p-2 rounded-lg">
                  <p className="text-xs text-white/50 mb-1">EXIT</p>
                  <div className="space-y-0.5">
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Date:</span>
                      <span className="text-xs text-white">{trade.exit_date}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Price:</span>
                      <span className="text-xs text-white">${trade.exit_price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Shares:</span>
                      <span className="text-xs text-white">{trade.shares}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-xs text-white/50">Value:</span>
                      <span className="text-xs text-white">
                        ${(trade.exit_price * trade.shares).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Trade Reasoning */}
              <div className="border-t border-white/10 pt-2 space-y-1">
                <div className="flex items-start gap-2">
                  <div className="flex-1">
                    <p className="text-xs text-white/50">Entry Reason:</p>
                    <p className="text-xs text-white">{trade.entry_reason}</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="flex-1">
                    <p className="text-xs text-white/50">Exit Reason:</p>
                    <p className="text-xs text-white capitalize">
                      {trade.exit_reason.replace('_', ' ')}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="flex-1">
                    <p className="text-xs text-white/50">Capital Impact:</p>
                    <p className="text-xs text-white">
                      ${trade.capital_before.toLocaleString()} → ${trade.capital_after.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {!showAllTrades && trades.length > 5 && (
          <div className="mt-3 text-center">
            <button
              onClick={() => setShowAllTrades(true)}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors"
            >
              View {trades.length - 5} More Trades
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
