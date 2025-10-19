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

export default function AdditionalInfoCharts({ additionalInfo }) {
  if (!additionalInfo || additionalInfo.length === 0) return null

  // Determine what type of chart to show based on data keys
  const samplePoint = additionalInfo[0]
  const hasRSI = 'rsi' in samplePoint
  const hasMACD = 'macd' in samplePoint
  const hasSMA = 'sma_20' in samplePoint && 'sma_50' in samplePoint
  const hasTwitterSentiment = 'twitter_sentiment' in samplePoint
  const hasRedditSentiment = 'reddit_sentiment' in samplePoint

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-light text-white">Strategy Insights</h2>
        <p className="text-xs text-white/50">Visual analysis of key indicators</p>
      </div>

      {/* RSI Chart */}
      {hasRSI && (
        <div className="bg-white/5 rounded-lg p-3 border border-white/10">
          <h3 className="text-sm font-light text-white mb-3">RSI (Relative Strength Index)</h3>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={additionalInfo}>
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
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />

              {/* Oversold/Overbought zones */}
              <Area
                dataKey={() => 30}
                fill="#ef4444"
                fillOpacity={0.1}
                stroke="none"
                name="Oversold Zone"
              />
              <Area
                dataKey={() => 70}
                fill="#22c55e"
                fillOpacity={0.1}
                stroke="none"
                name="Overbought Zone"
              />

              {/* Reference lines for thresholds */}
              {samplePoint.rsi_threshold && (
                <ReferenceLine
                  y={samplePoint.rsi_threshold}
                  stroke="#ef4444"
                  strokeDasharray="5 5"
                  label={{ value: `Entry: ${samplePoint.rsi_threshold}`, fill: '#ef4444', fontSize: 12 }}
                />
              )}
              {samplePoint.rsi_exit_threshold && (
                <ReferenceLine
                  y={samplePoint.rsi_exit_threshold}
                  stroke="#22c55e"
                  strokeDasharray="5 5"
                  label={{ value: `Exit: ${samplePoint.rsi_exit_threshold}`, fill: '#22c55e', fontSize: 12 }}
                />
              )}

              {/* RSI line */}
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="RSI"
              />
            </ComposedChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-400 mt-2">
            RSI measures momentum. Values below 30 indicate oversold (potential buy), above 70 indicates overbought (potential sell).
          </p>
        </div>
      )}

      {/* MACD Chart */}
      {hasMACD && (
        <div className="bg-white/5 rounded-lg p-3 border border-white/10">
          <h3 className="text-sm font-light text-white mb-3">MACD (Moving Average Convergence Divergence)</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={additionalInfo}>
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
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <ReferenceLine y={0} stroke="#666" />
              <Line
                type="monotone"
                dataKey="macd"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="MACD"
              />
              <Line
                type="monotone"
                dataKey="macd_signal"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name="Signal Line"
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-400 mt-2">
            MACD crossovers indicate trend changes. Bullish when MACD crosses above signal line, bearish when below.
          </p>
        </div>
      )}

      {/* SMA Chart */}
      {hasSMA && (
        <div className="bg-white/5 rounded-lg p-3 border border-white/10">
          <h3 className="text-sm font-light text-white mb-3">Simple Moving Averages</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={additionalInfo}>
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
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={false}
                name="Price"
              />
              <Line
                type="monotone"
                dataKey="sma_20"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="SMA 20"
              />
              <Line
                type="monotone"
                dataKey="sma_50"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name="SMA 50"
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-400 mt-2">
            Moving averages smooth price trends. Bullish when short-term (SMA 20) crosses above long-term (SMA 50).
          </p>
        </div>
      )}

      {/* Twitter Sentiment Chart */}
      {hasTwitterSentiment && (
        <div className="bg-white/5 rounded-lg p-3 border border-white/10">
          <h3 className="text-sm font-light text-white mb-3">Twitter Sentiment Score</h3>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={additionalInfo}>
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
                domain={[-1, 1]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />

              {/* Sentiment zones */}
              <Area
                dataKey={() => 0}
                fill="#ef4444"
                fillOpacity={0.1}
                stroke="none"
                name="Negative Zone"
              />
              <Area
                dataKey={() => 1}
                fill="#22c55e"
                fillOpacity={0.1}
                stroke="none"
                name="Positive Zone"
              />

              <ReferenceLine y={0} stroke="#666" label={{ value: 'Neutral', fill: '#666', fontSize: 12 }} />
              {samplePoint.twitter_threshold && (
                <ReferenceLine
                  y={samplePoint.twitter_threshold}
                  stroke="#22c55e"
                  strokeDasharray="5 5"
                  label={{ value: `Threshold: ${samplePoint.twitter_threshold}`, fill: '#22c55e', fontSize: 12 }}
                />
              )}

              <Line
                type="monotone"
                dataKey="twitter_sentiment"
                stroke="#1DA1F2"
                strokeWidth={2}
                dot={false}
                name="Twitter Sentiment"
              />
            </ComposedChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-400 mt-2">
            Sentiment ranges from -1 (very negative) to +1 (very positive). Current sentiment is used as proxy for historical dates.
          </p>
        </div>
      )}

      {/* Reddit Sentiment Chart */}
      {hasRedditSentiment && (
        <div className="bg-white/5 rounded-lg p-3 border border-white/10">
          <h3 className="text-sm font-light text-white mb-3">Reddit Sentiment Score</h3>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={additionalInfo}>
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
                domain={[-1, 1]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />

              {/* Sentiment zones */}
              <Area
                dataKey={() => 0}
                fill="#ef4444"
                fillOpacity={0.1}
                stroke="none"
                name="Negative Zone"
              />
              <Area
                dataKey={() => 1}
                fill="#22c55e"
                fillOpacity={0.1}
                stroke="none"
                name="Positive Zone"
              />

              <ReferenceLine y={0} stroke="#666" label={{ value: 'Neutral', fill: '#666', fontSize: 12 }} />
              {samplePoint.reddit_threshold && (
                <ReferenceLine
                  y={samplePoint.reddit_threshold}
                  stroke="#22c55e"
                  strokeDasharray="5 5"
                  label={{ value: `Threshold: ${samplePoint.reddit_threshold}`, fill: '#22c55e', fontSize: 12 }}
                />
              )}

              <Line
                type="monotone"
                dataKey="reddit_sentiment"
                stroke="#FF4500"
                strokeWidth={2}
                dot={false}
                name="Reddit Sentiment"
              />
            </ComposedChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-400 mt-2">
            Sentiment ranges from -1 (very negative) to +1 (very positive). Shows why trades may/may not execute based on sentiment threshold.
          </p>
        </div>
      )}

      {/* Info box if no additional data */}
      {!hasRSI && !hasMACD && !hasSMA && !hasTwitterSentiment && !hasRedditSentiment && (
        <div className="bg-dark-surface rounded-lg p-6 border border-dark-border text-center">
          <p className="text-gray-400">No additional indicator data available for this strategy.</p>
        </div>
      )}
    </div>
  )
}
