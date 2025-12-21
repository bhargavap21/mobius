import PropTypes from 'prop-types'

function EvaluationResults({ evaluationResults }) {
  if (!evaluationResults) return null

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-6 mt-6">
      <h2 className="text-xl font-semibold text-white mb-4">Evaluation Results</h2>

      <div className="space-y-4">
        {evaluationResults.metrics && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(evaluationResults.metrics).map(([key, value]) => (
              <div key={key} className="bg-dark-bg p-4 rounded-lg">
                <div className="text-gray-400 text-sm mb-1">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                <div className="text-white text-lg font-semibold">
                  {typeof value === 'number' ? value.toFixed(2) : value}
                </div>
              </div>
            ))}
          </div>
        )}

        {evaluationResults.summary && (
          <div className="bg-dark-bg p-4 rounded-lg">
            <h3 className="text-white font-medium mb-2">Summary</h3>
            <p className="text-gray-300">{evaluationResults.summary}</p>
          </div>
        )}

        {evaluationResults.details && (
          <div className="bg-dark-bg p-4 rounded-lg">
            <h3 className="text-white font-medium mb-2">Details</h3>
            <pre className="text-gray-300 text-sm overflow-x-auto">
              {JSON.stringify(evaluationResults.details, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

EvaluationResults.propTypes = {
  evaluationResults: PropTypes.shape({
    metrics: PropTypes.object,
    summary: PropTypes.string,
    details: PropTypes.any
  })
}

export default EvaluationResults
