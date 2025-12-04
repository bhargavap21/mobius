import { useState } from 'react'
import { ChevronDownIcon, ChevronRightIcon, CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

export default function EvaluationResults({ evaluationResults }) {
  const [expanded, setExpanded] = useState(true)
  const [expandedEvaluators, setExpandedEvaluators] = useState({})

  if (!evaluationResults) {
    return null
  }

  const toggleEvaluator = (name) => {
    setExpandedEvaluators(prev => ({
      ...prev,
      [name]: !prev[name]
    }))
  }

  const { all_passed, average_score, failed_evaluators, passed_evaluators, errors, warnings, results } = evaluationResults

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-6 mb-6">
      {/* Header */}
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          {all_passed ? (
            <CheckCircleIcon className="w-6 h-6 text-green-500" />
          ) : (
            <XCircleIcon className="w-6 h-6 text-red-500" />
          )}
          <div>
            <h3 className="text-lg font-semibold text-white">
              Strategy Evaluation
            </h3>
            <p className="text-sm text-gray-400">
              {all_passed ? 'All checks passed' : `${failed_evaluators?.length || 0} checks failed`}
              {average_score !== undefined && ` • Score: ${average_score.toFixed(1)}/1.0`}
            </p>
          </div>
        </div>
        {expanded ? (
          <ChevronDownIcon className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRightIcon className="w-5 h-5 text-gray-400" />
        )}
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="mt-6 space-y-4">
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-2xl font-bold text-green-500">{passed_evaluators?.length || 0}</div>
              <div className="text-sm text-gray-400">Passed</div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-2xl font-bold text-red-500">{failed_evaluators?.length || 0}</div>
              <div className="text-sm text-gray-400">Failed</div>
            </div>
            <div className="bg-dark-bg rounded-lg p-4">
              <div className="text-2xl font-bold text-purple-500">{average_score?.toFixed(2) || '0.00'}</div>
              <div className="text-sm text-gray-400">Avg Score</div>
            </div>
          </div>

          {/* Errors (if any) */}
          {errors && errors.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <XCircleIcon className="w-5 h-5 text-red-500" />
                <h4 className="font-semibold text-red-500">Errors Found</h4>
              </div>
              <ul className="space-y-1 text-sm text-red-400">
                {errors.slice(0, 10).map((error, idx) => (
                  <li key={idx} className="ml-7">• {error}</li>
                ))}
                {errors.length > 10 && (
                  <li className="ml-7 text-gray-400 italic">... and {errors.length - 10} more</li>
                )}
              </ul>
            </div>
          )}

          {/* Warnings (if any) */}
          {warnings && warnings.length > 0 && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
                <h4 className="font-semibold text-yellow-500">Warnings</h4>
              </div>
              <ul className="space-y-1 text-sm text-yellow-400">
                {warnings.slice(0, 5).map((warning, idx) => (
                  <li key={idx} className="ml-7">• {warning}</li>
                ))}
                {warnings.length > 5 && (
                  <li className="ml-7 text-gray-400 italic">... and {warnings.length - 5} more</li>
                )}
              </ul>
            </div>
          )}

          {/* Individual Evaluator Results */}
          {results && Object.keys(results).length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-gray-300 mb-3">Detailed Results</h4>
              {Object.entries(results).map(([name, result]) => (
                <div
                  key={name}
                  className="bg-dark-bg rounded-lg border border-dark-border overflow-hidden"
                >
                  {/* Evaluator Header */}
                  <div
                    className="flex items-center justify-between p-4 cursor-pointer hover:bg-dark-hover transition-colors"
                    onClick={() => toggleEvaluator(name)}
                  >
                    <div className="flex items-center gap-3">
                      {result.passed ? (
                        <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0" />
                      ) : (
                        <XCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0" />
                      )}
                      <div>
                        <div className="font-medium text-white">{name}</div>
                        {result.score !== undefined && (
                          <div className="text-xs text-gray-400">Score: {result.score.toFixed(2)}</div>
                        )}
                      </div>
                    </div>
                    {expandedEvaluators[name] ? (
                      <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRightIcon className="w-4 h-4 text-gray-400" />
                    )}
                  </div>

                  {/* Evaluator Details */}
                  {expandedEvaluators[name] && (
                    <div className="px-4 pb-4 space-y-3 border-t border-dark-border pt-3">
                      {/* Errors */}
                      {result.errors && result.errors.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-red-400 mb-1">Errors:</div>
                          <ul className="space-y-1 text-xs text-red-300">
                            {result.errors.map((error, idx) => (
                              <li key={idx} className="ml-4">• {error}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Warnings */}
                      {result.warnings && result.warnings.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-yellow-400 mb-1">Warnings:</div>
                          <ul className="space-y-1 text-xs text-yellow-300">
                            {result.warnings.map((warning, idx) => (
                              <li key={idx} className="ml-4">• {warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Details */}
                      {result.details && Object.keys(result.details).length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-gray-400 mb-1">Details:</div>
                          <div className="bg-dark-card rounded p-2 text-xs font-mono text-gray-300">
                            <pre className="whitespace-pre-wrap overflow-x-auto">
                              {JSON.stringify(result.details, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* If passed with no details */}
                      {result.passed && (!result.errors || result.errors.length === 0) && (!result.warnings || result.warnings.length === 0) && (
                        <div className="text-xs text-green-400">
                          ✓ All checks passed
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
