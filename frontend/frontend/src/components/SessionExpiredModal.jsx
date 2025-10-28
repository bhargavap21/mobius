export default function SessionExpiredModal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-dark-surface border border-dark-border rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 rounded-full bg-accent-danger/10 border-2 border-accent-danger/30 flex items-center justify-center">
            <svg className="w-8 h-8 text-accent-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        </div>

        {/* Content */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">Session Expired</h2>
          <p className="text-white/70 text-sm leading-relaxed">
            Your login session has expired for security reasons. Please sign in again to continue using Mobius.
          </p>
        </div>

        {/* Button */}
        <button
          onClick={onClose}
          className="w-full bg-accent-primary hover:bg-accent-primary-dark text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2 focus:ring-offset-dark-surface"
        >
          Sign In Again
        </button>
      </div>
    </div>
  )
}
