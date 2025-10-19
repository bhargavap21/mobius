import { useState, useEffect } from 'react'

export default function ProgressIndicator() {
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    { icon: 'PARSE', label: 'Parsing Strategy', desc: 'Understanding your trading rules...' },
    { icon: 'CODE', label: 'Generating Code', desc: 'Creating strategy implementation...' },
    { icon: 'TEST', label: 'Running Backtest', desc: 'Testing strategy on historical data...' },
    { icon: 'ANALYZE', label: 'Analyzing Results', desc: 'Evaluating performance metrics...' },
    { icon: 'REFINE', label: 'Refining Strategy', desc: 'Optimizing parameters...' },
  ]

  useEffect(() => {
    // Cycle through steps every 8 seconds
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length)
    }, 8000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="w-full max-w-md">
      <div className="space-y-3">
        {steps.map((step, idx) => {
          const isActive = idx === currentStep
          const isPast = idx < currentStep
          const isFuture = idx > currentStep

          return (
            <div
              key={idx}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                isActive
                  ? 'bg-accent-primary/10 border-2 border-accent-primary/30 scale-105'
                  : isPast
                  ? 'bg-green-500/5 border border-green-500/20 opacity-60'
                  : 'bg-dark-bg border border-dark-border opacity-40'
              }`}
            >
              <div
                className={`text-sm font-mono transition-transform duration-500 ${
                  isActive ? 'scale-125' : 'scale-100'
                } ${isPast ? 'text-green-400' : 'text-gray-400'}`}
              >
                {isPast ? 'DONE' : step.icon}
              </div>
              <div className="flex-1">
                <p
                  className={`font-light text-base ${
                    isActive ? 'text-fg' : 'text-fg-muted'
                  }`}
                >
                  {step.label}
                </p>
                {isActive && (
                  <p className="text-sm text-fg-muted mt-1">{step.desc}</p>
                )}
              </div>
              {isActive && (
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse"></div>
                  <div
                    className="w-2 h-2 bg-accent-primary rounded-full animate-pulse"
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-accent-primary rounded-full animate-pulse"
                    style={{ animationDelay: '0.4s' }}
                  ></div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-fg-muted">
          This may take 30-60 seconds for complex strategies
        </p>
      </div>
    </div>
  )
}
