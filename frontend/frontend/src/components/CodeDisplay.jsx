import { useState } from 'react'

export default function CodeDisplay({ code, strategyName }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([code], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${strategyName?.replace(/\s+/g, '_').toLowerCase() || 'trading_bot'}.py`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const lineCount = code?.split('\n').length || 0

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-light text-fg">🐍 Generated Python Code</h2>
          <p className="text-sm text-fg-muted mt-1">
            {lineCount} lines • Ready to use
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="btn btn-secondary text-sm flex items-center gap-2"
          >
            {copied ? (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy Code
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="btn btn-primary text-sm flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </button>
        </div>
      </div>

      {/* Code Block */}
      <div className="relative">
        <pre className="bg-dark-bg rounded-lg border border-dark-border p-4 overflow-x-auto text-sm">
          <code className="text-gray-300 font-mono">{code}</code>
        </pre>

        {/* Line numbers overlay */}
        <div className="absolute top-0 left-0 p-4 text-gray-600 font-mono text-sm select-none pointer-events-none">
          {code?.split('\n').map((_, i) => (
            <div key={i} className="leading-6">{i + 1}</div>
          ))}
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="mt-6 p-4 bg-dark-bg/50 rounded-lg">
        <h3 className="text-base font-light text-fg mb-2">🚀 How to use this code:</h3>
        <ol className="text-sm text-fg-muted space-y-2 list-decimal list-inside">
          <li>Download the generated Python file</li>
          <li>Install required packages: <code className="px-2 py-1 bg-dark-bg rounded text-accent">pip install alpaca-py tweepy textblob python-dotenv</code></li>
          <li>Add your API keys to <code className="px-2 py-1 bg-dark-bg rounded text-accent">.env</code> file</li>
          <li>Run: <code className="px-2 py-1 bg-dark-bg rounded text-accent">python {strategyName?.replace(/\s+/g, '_').toLowerCase() || 'trading_bot'}.py</code></li>
        </ol>
      </div>
    </div>
  )
}
