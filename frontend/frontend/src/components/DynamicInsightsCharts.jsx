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
    return null
  }

  if (!insightsConfig || !insightsConfig.visualizations || insightsConfig.visualizations.length === 0) {
    // Fallback to automatic detection if no config provided
    return <AdditionalInfoChartsLegacy additionalInfo={additionalInfo} />
  }

  return (
    <div className="bg-dark-card rounded-xl border border-dark-border p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">📊 Strategy Insights</h2>
        <p className="text-sm text-gray-400">AI-generated visualizations</p>
      </div>

      {/* General insights from LLM */}
      {insightsConfig.insights && insightsConfig.insights.length > 0 && (
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-400 mb-2">💡 Key Insights</h3>
          <ul className="space-y-1">
            {insightsConfig.insights.map((insight, idx) => (
              <li key={idx} className="text-sm text-gray-300">• {insight}</li>
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

  // Check if data has the required metrics
  const hasData = data.some(point => primaryMetric in point)

  if (!hasData) {
    return (
      <div className="bg-dark-surface rounded-lg p-4 border border-dark-border">
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-gray-400">{description}</p>
        <p className="text-sm text-yellow-500 mt-2">⚠️ No data available for this visualization</p>
      </div>
    )
  }

  // Get y-axis config
  const yAxisConfig = chart_config?.y_axis || {}
  const yDomain = yAxisConfig.min !== undefined && yAxisConfig.max !== undefined
    ? [yAxisConfig.min, yAxisConfig.max]
    : undefined

  return (
    <div className="bg-dark-surface rounded-lg p-4 border border-dark-border">
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-gray-400 mb-4">{description}</p>

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

          {/* Main metric line */}
          <Line
            type="monotone"
            dataKey={primaryMetric}
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name={primaryMetric.replace(/_/g, ' ').toUpperCase()}
          />

          {/* Additional metrics */}
          {additionalMetrics.map((metric, metricIdx) => (
            <Line
              key={`metric-${metricIdx}`}
              type="monotone"
              dataKey={metric}
              stroke={metricIdx === 0 ? '#ef4444' : '#22c55e'}
              strokeWidth={2}
              dot={false}
              name={metric.replace(/_/g, ' ').toUpperCase()}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>
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
