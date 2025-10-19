export default function CodeDisplay({ code, strategyName }) {
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
    <div className="rounded-2xl border border-white/10 bg-[#0e1117] p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-light text-white">Generated Python Code</h2>
        <button
          onClick={handleDownload}
          className="px-4 py-2 text-sm font-medium rounded-lg bg-accent/10 text-accent hover:bg-accent/20 transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download
        </button>
      </div>

      <p className="text-xs text-white/50 mb-4">
        {lineCount} lines • Ready to download
      </p>

      {/* Usage Instructions */}
      <div className="mt-4 p-3 bg-white/5 rounded-lg border border-white/10">
        <h3 className="text-sm font-light text-white mb-2">How to use this code:</h3>
        <ol className="text-xs text-white/70 space-y-2 list-decimal list-inside">
          <li>Download the generated Python file</li>
          <li>Install required packages: <code className="px-2 py-1 bg-black/30 rounded text-accent text-xs">pip install alpaca-py tweepy textblob python-dotenv</code></li>
          <li>Add your API keys to <code className="px-2 py-1 bg-black/30 rounded text-accent text-xs">.env</code> file</li>
          <li>Run: <code className="px-2 py-1 bg-black/30 rounded text-accent text-xs">python {strategyName?.replace(/\s+/g, '_').toLowerCase() || 'trading_bot'}.py</code></li>
        </ol>
      </div>
    </div>
  )
}
