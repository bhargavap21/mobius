export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-dark-border rounded-full"></div>
        <div className="w-16 h-16 border-4 border-accent-primary border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
      </div>
      <div className="text-center">
        <p className="text-2xl font-light text-fg">Generating Your Trading Bot...</p>
        <p className="text-base text-fg-muted mt-1">AI is analyzing your strategy and writing code</p>
      </div>
      <div className="flex gap-2 mt-2">
        <div className="w-2 h-2 bg-accent-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-accent-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-accent-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
    </div>
  )
}
