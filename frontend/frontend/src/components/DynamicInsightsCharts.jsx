import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Area, ComposedChart } from 'recharts'

// Custom tooltip defined outside component to avoid React version issues
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-dark-surface border border-dark-border rounded-lg p-3 shadow-lg">
        <p className="text-white font-semibold mb-2">{data.date}</p>
        <p className="text-gray-400 text-xs mb-1">
          Price: ${data.price?.toFixed(2)}
        </p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}: {entry.value?.toFixed(entry.name.includes('sentiment') ? 3 : 2)}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export default function DynamicInsightsCharts({ additionalInfo, insightsConfig }) {
  if (!additionalInfo || additionalInfo.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-light text-white">Strategy Insights</h2>
          <p className="text-xs text-white/50">AI-generated visualizations</p>
        </div>
        <div className="bg-accent/10 border border-accent/30 rounded-lg p-3">
          <p className="text-sm text-accent font-medium">Strategy processing in progress</p>
          <p className="text-xs text-accent/80 mt-1">
            Additional insights and visualizations will appear here once the strategy analysis is complete.
            This may take a few moments while we analyze market data and generate trade signals.
          </p>
        </div>
      </div>
    )
  }

  if (!insightsConfig || !insightsConfig.visualizations || insightsConfig.visualizations.length === 0) {
    // Fallback to automatic detection if no config provided
    return <AdditionalInfoChartsLegacy additionalInfo={additionalInfo} />
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-light text-white">Strategy Insights</h2>
        <p className="text-xs text-white/50">AI-generated visualizations</p>
      </div>

      {/* General insights from LLM */}
      {insightsConfig.insights && insightsConfig.insights.length > 0 && (
        <div className="bg-accent/10 border border-accent/30 rounded-lg p-3">
          <h3 className="text-xs font-light text-accent mb-2">Key Insights</h3>
          <ul className="space-y-1">
            {insightsConfig.insights.map((insight, idx) => (
              <li key={idx} className="text-xs text-gray-300">• {insight}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Render each visualization */}
      {insightsConfig.visualizations.map((viz, idx) => (
        <RenderVisualization
          key={idx}
          visualization={viz}
          data={additionalInfo}
        />
      ))}
    </div>
  )
}

function RenderVisualization({ visualization, data }) {
  const { title, description, type, data_to_collect, chart_config } = visualization

  // Extract the metrics we need to display
  const primaryMetric = data_to_collect?.primary_metric
  const additionalMetrics = data_to_collect?.additional_metrics || []
  const thresholds = data_to_collect?.thresholds || {}

  // Debug logging (development only)
  if (process.env.NODE_ENV !== 'production' && data && data.length > 0) {
    console.log(`[Insights] ${title}:`, {
      primaryMetric,
      dataLength: data.length,
      firstDataPoint: data[0],
      availableFields: Object.keys(data[0] || {})
    })
  }

  // Check if data has the required metrics - more tolerant checking
  const hasData = data && data.length > 0 && data.some(point => {
    // If no primary metric specified, assume data is available if we have any datapoints with more than just date/price
    if (!primaryMetric) {
      // Check if we have any interesting data beyond the basics
      const keys = Object.keys(point)
      return keys.length > 2 || keys.some(k => k !== 'date' && k !== 'price')
    }
    
    // Check for direct metric match
    if (primaryMetric in point && point[primaryMetric] !== undefined && point[primaryMetric] !== null) return true
    
    // Check for common field name variations (normalize field names)
    // Handle sentiment-related fields
    if (primaryMetric.includes('sentiment') || primaryMetric.includes('tweet')) {
      if (point.tweet_sentiment_score !== undefined && point.tweet_sentiment_score !== null) return true
      if (point.sentimentScore !== undefined && point.sentimentScore !== null) return true
      if (point.sentiment !== undefined && point.sentiment !== null) return true
      if (point.twitter_sentiment !== undefined && point.twitter_sentiment !== null) return true
      if (point.reddit_sentiment !== undefined && point.reddit_sentiment !== null) return true
      if (point.wsb_sentiment_score !== undefined && point.wsb_sentiment_score !== null) return true
      if (point.elon_tweet_sentiment !== undefined && point.elon_tweet_sentiment !== null) return true
    }
    
    // Handle price-related fields
    if (primaryMetric.includes('price')) {
      if (point.price !== undefined && point.price !== null) return true
      if (point.close !== undefined && point.close !== null) return true
      if (point.gme_price !== undefined && point.gme_price !== null) return true
    }
    
    // Handle RSI
    if (primaryMetric.includes('rsi') || primaryMetric.includes('RSI')) {
      if (point.rsi !== undefined && point.rsi !== null) return true
      if (point.RSI !== undefined && point.RSI !== null) return true
    }
    
    // Handle MACD
    if (primaryMetric.includes('macd') || primaryMetric.includes('MACD')) {
      if (point.macd !== undefined && point.macd !== null) return true
      if (point.MACD !== undefined && point.MACD !== null) return true
    }
    
    // Handle PnL/profit/loss related fields
    if (primaryMetric.includes('pnl') || primaryMetric.includes('profit') || primaryMetric.includes('loss') || primaryMetric.includes('return')) {
      if (point.pnl !== undefined && point.pnl !== null) return true
      if (point.pnl_pct !== undefined && point.pnl_pct !== null) return true
      if (point.profit !== undefined && point.profit !== null) return true
      if (point.return !== undefined && point.return !== null) return true
      if (point.trade_pnl !== undefined && point.trade_pnl !== null) return true
      if (point.trade_pnl_percentage !== undefined && point.trade_pnl_percentage !== null) return true
      if (point.trade_return !== undefined && point.trade_return !== null) return true
      // Check if we have trade markers with PnL info
      if (point.trade_entry !== undefined && point.trade_entry !== null) return true
      if (point.trade_exit !== undefined && point.trade_exit !== null) return true
    }
    
    // Check for trade-related metrics
    if (primaryMetric === 'trade_positions' && point.has_position !== undefined) return true
    if (primaryMetric === 'stop_loss_level' && point.stop_loss_level !== undefined) return true
    if (primaryMetric === 'exit_condition_analysis' && (point.trade_entry !== null || point.trade_exit !== null)) return true
    if (primaryMetric === 'exit_type_percentage' && point.exit_type_percentage !== undefined) return true
    if (primaryMetric === 'tweet_timing' && point.tweet_timing !== undefined) return true
    
    // Handle volume
    if (primaryMetric.includes('volume')) {
      if (point.volume !== undefined && point.volume !== null) return true
      if (point.Volume !== undefined && point.Volume !== null) return true
    }
    
    return false
  })


  // Get y-axis config
  const yAxisConfig = chart_config?.y_axis || {}
  const yDomain = yAxisConfig.min !== undefined && yAxisConfig.max !== undefined
    ? [yAxisConfig.min, yAxisConfig.max]
    : undefined

  return (
    <div className="bg-white/5 rounded-lg p-3 border border-white/10">
      <h3 className="text-sm font-light text-white mb-1">{title}</h3>
      <p className="text-xs text-white/50 mb-3">{description}</p>

      <div className="relative">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="date"
              stroke="#888"
              tick={{ fill: '#888', fontSize: 12 }}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getMonth() + 1}/${date.getDate()}`
              }}
            />
            <YAxis
              stroke="#888"
              tick={{ fill: '#888', fontSize: 12 }}
              domain={yDomain}
              label={yAxisConfig.label ? { value: yAxisConfig.label, angle: -90, position: 'insideLeft', style: { fill: '#888' } } : undefined}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} iconType="line" />

            {/* Render zones if specified */}
            {chart_config?.zones && chart_config.zones.map((zone, zoneIdx) => (
              <Area
                key={`zone-${zoneIdx}`}
                dataKey={() => zone.end}
                fill={zone.color === 'red' ? '#ef4444' : zone.color === 'green' ? '#22c55e' : '#3b82f6'}
                fillOpacity={0.1}
                stroke="none"
                name={zone.label}
              />
            ))}

            {/* Render reference lines for thresholds */}
            {chart_config?.reference_lines && chart_config.reference_lines.map((refLine, refIdx) => {
              // Try to find the threshold value in the data
              const thresholdKey = refLine.key
              const thresholdValue = data[0]?.[thresholdKey]

              if (thresholdValue !== undefined) {
                return (
                  <ReferenceLine
                    key={`ref-${refIdx}`}
                    y={thresholdValue}
                    stroke={refLine.color === 'green' ? '#22c55e' : refLine.color === 'red' ? '#ef4444' : '#3b82f6'}
                    strokeDasharray="5 5"
                    label={{ value: refLine.label, fill: refLine.color === 'green' ? '#22c55e' : refLine.color === 'red' ? '#ef4444' : '#3b82f6', fontSize: 12 }}
                  />
                )
              }
              return null
            })}

            {/* Only render data lines if data is available */}
            {hasData && (
              <>
                {/* Main metric line - handle complex data structures */}
                {primaryMetric === 'exit_type_percentage' ? (
                  <>
                    <Line
                      type="monotone"
                      dataKey={(point) => point.exit_type_percentage?.profit_target || 0}
                      stroke="#22c55e"
                      strokeWidth={2}
                      dot={false}
                      name="Profit Target %"
                    />
                    <Line
                      type="monotone"
                      dataKey={(point) => point.exit_type_percentage?.stop_loss || 0}
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={false}
                      name="Stop Loss %"
                    />
                  </>
                ) : primaryMetric === 'tweet_timing' ? (
                  <>
                    <Line
                      type="monotone"
                      dataKey={(point) => point.tweet_timing?.market_hours || 0}
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                      name="Market Hours %"
                    />
                    <Line
                      type="monotone"
                      dataKey={(point) => point.tweet_timing?.after_hours || 0}
                      stroke="#f59e0b"
                      strokeWidth={2}
                      dot={false}
                      name="After Hours %"
                    />
                  </>
                ) : (
                  <Line
                    type="monotone"
                    dataKey={(point) => {
                      // Try primary metric first
                      if (point[primaryMetric] !== undefined) return point[primaryMetric]
                      
                      // Fallback to common field name variations
                      if (primaryMetric.includes('sentiment') || primaryMetric.includes('tweet')) {
                        return point.tweet_sentiment_score ?? point.sentimentScore ?? point.sentiment ?? point.twitter_sentiment ?? point.reddit_sentiment ?? 0
                      }
                      if (primaryMetric.includes('price')) {
                        return point.price ?? point.close ?? 0
                      }
                      if (primaryMetric.includes('rsi')) {
                        return point.rsi ?? point.RSI ?? 0
                      }
                      if (primaryMetric.includes('macd')) {
                        return point.macd ?? point.MACD ?? 0
                      }
                      if (primaryMetric.includes('pnl') || primaryMetric.includes('profit') || primaryMetric.includes('loss') || primaryMetric.includes('return')) {
                        // Try direct fields first
                        if (point.pnl !== undefined) return point.pnl
                        if (point.pnl_pct !== undefined) return point.pnl_pct
                        if (point.profit !== undefined) return point.profit
                        if (point.return !== undefined) return point.return
                        if (point.trade_pnl !== undefined) return point.trade_pnl
                        if (point.trade_pnl_percentage !== undefined) return point.trade_pnl_percentage
                        if (point.trade_return !== undefined) return point.trade_return
                        // Extract from trade_exit marker if available
                        if (point.trade_exit && point.trade_exit.pnl_pct !== undefined) return point.trade_exit.pnl_pct
                        // Only show value on exit points, otherwise null to create gaps
                        return null
                      }
                      if (primaryMetric.includes('volume')) {
                        return point.volume ?? point.Volume ?? 0
                      }
                      
                      return 0
                    }}
                    stroke="#7c3aed"
                    strokeWidth={2}
                    dot={(props) => {
                      // Show dots on trade exit points
                      const { cx, cy, payload } = props
                      if (payload && payload.trade_exit) {
                        const pnl = payload.trade_exit.pnl_pct || 0
                        const color = pnl >= 0 ? '#22c55e' : '#ef4444'
                        return (
                          <circle
                            cx={cx}
                            cy={cy}
                            r={5}
                            fill={color}
                            stroke="#fff"
                            strokeWidth={2}
                          />
                        )
                      }
                      return null
                    }}
                    connectNulls={false}
                    name={primaryMetric.replace(/_/g, ' ').toUpperCase()}
                  />
                )}

                {/* Trade position visualizations */}
                {primaryMetric === 'trade_positions' && (
                  <>
                    {/* Stop loss level */}
                    <Line
                      type="monotone"
                      dataKey="stop_loss_level"
                      stroke="#ef4444"
                      strokeWidth={1}
                      strokeDasharray="5 5"
                      dot={false}
                      name="Stop Loss Level"
                    />
                    {/* Take profit level */}
                    <Line
                      type="monotone"
                      dataKey="take_profit_level"
                      stroke="#22c55e"
                      strokeWidth={1}
                      strokeDasharray="5 5"
                      dot={false}
                      name="Take Profit Level"
                    />
                    {/* Position entry price */}
                    <Line
                      type="monotone"
                      dataKey="position_entry_price"
                      stroke="#f59e0b"
                      strokeWidth={2}
                      strokeDasharray="10 5"
                      dot={false}
                      name="Entry Price"
                    />
                  </>
                )}

                {/* Additional metrics */}
                {additionalMetrics.map((metric, metricIdx) => (
                  <Line
                    key={`metric-${metricIdx}`}
                    type="monotone"
                    dataKey={(point) => {
                      // Try direct metric first
                      if (point[metric] !== undefined) return point[metric]
                      
                      // Handle common variations for additional metrics
                      if (metric.includes('price')) {
                        return point.price ?? point.close ?? 0
                      }
                      if (metric.includes('rsi')) {
                        return point.rsi ?? point.RSI ?? 0
                      }
                      if (metric.includes('macd')) {
                        return point.macd ?? point.MACD ?? 0
                      }
                      
                      return 0
                    }}
                    stroke={metricIdx === 0 ? '#ffffff' : metricIdx === 1 ? '#22c55e' : '#3b82f6'}
                    strokeWidth={2}
                    dot={false}
                    name={metric.replace(/_/g, ' ').toUpperCase()}
                  />
                ))}
              </>
            )}
          </ComposedChart>
        </ResponsiveContainer>

        {/* Overlay message when no data is available */}
        {!hasData && (
          <div className="absolute inset-0 flex items-center justify-center bg-dark-surface/80 backdrop-blur-sm">
            <div className="text-center p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg max-w-md">
              <p className="text-sm text-yellow-400 font-medium mb-2">⚠️ Data not yet available</p>
              <p className="text-xs text-yellow-300 mb-2">
                This visualization requires <span className="font-mono text-yellow-200">{primaryMetric}</span> data that hasn't been generated yet.
              </p>
              <p className="text-xs text-yellow-300">
                This typically happens when the strategy is still processing or no trades match the conditions.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Fallback to legacy detection-based rendering
function AdditionalInfoChartsLegacy({ additionalInfo }) {
  // Import and render the original AdditionalInfoCharts logic here if needed
  return (
    <div className="bg-dark-surface rounded-lg p-4 border border-dark-border text-center">
      <p className="text-gray-400 text-sm">Using automatic chart detection (legacy mode)</p>
    </div>
  )
}
