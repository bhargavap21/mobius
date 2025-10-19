import { useState, useEffect } from 'react'

export default function AgentActivityLog({ sessionId }) {
  const [events, setEvents] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [isConnecting, setIsConnecting] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!sessionId) {
      console.log('[AgentActivityLog] No session ID provided')
      return
    }

    console.log('[AgentActivityLog] Setting up SSE connection for:', sessionId)
    setIsConnecting(true)
    setError(null)

    // Add a small delay to avoid StrictMode double-mount issues
    const timeoutId = setTimeout(() => {
      console.log('[AgentActivityLog] Creating EventSource...')

      const url = `http://localhost:8000/api/strategy/progress/${sessionId}`
      console.log('[AgentActivityLog] SSE URL:', url)

      // Test if we can reach the endpoint first
      fetch(url.replace('/progress/', '/health'))
        .then(res => console.log('[AgentActivityLog] Health check:', res.status))
        .catch(err => console.error('[AgentActivityLog] Health check failed:', err))

      let eventSource
      try {
        eventSource = new EventSource(url)
        console.log('[AgentActivityLog] EventSource created, readyState:', eventSource.readyState)
        console.log('[AgentActivityLog] EventSource URL:', eventSource.url)
      } catch (error) {
        console.error('[AgentActivityLog] Failed to create EventSource:', error)
        setError('Failed to create connection')
        setIsConnecting(false)
        return
      }

      eventSource.onopen = () => {
        console.log('[AgentActivityLog] SSE connection opened successfully!')
        setIsConnecting(false)
      }

      eventSource.onmessage = (event) => {
        try {
          console.log('[AgentActivityLog] Received event:', event.data)
          const data = JSON.parse(event.data)

          // Handle initial connection message
          if (data.type === 'connected') {
            console.log('[AgentActivityLog] Connected to activity stream')
            setIsConnecting(false)
            return
          }

          setEvents((prev) => [...prev, data])

          // Check if workflow is complete
          if (data.type === 'complete' || data.type === 'error') {
            setIsComplete(true)
            eventSource.close()
          }
        } catch (error) {
          console.error('[AgentActivityLog] Error parsing SSE event:', error)
        }
      }

      eventSource.onerror = (error) => {
        console.error('[AgentActivityLog] SSE error details:', {
          error,
          readyState: eventSource.readyState,
          url: eventSource.url,
          withCredentials: eventSource.withCredentials
        })

        // Check readyState to determine error type
        if (eventSource.readyState === EventSource.CONNECTING) {
          console.log('[AgentActivityLog] Still trying to connect...')
        } else if (eventSource.readyState === EventSource.CLOSED) {
          console.log('[AgentActivityLog] Connection closed')
          setIsConnecting(false)
          setError('Connection closed')
        }
      }

      // Store eventSource in closure for cleanup
      return () => {
        console.log('[AgentActivityLog] Cleanup called, closing EventSource')
        if (eventSource) {
          eventSource.close()
        }
      }
    }, 100) // Small delay to avoid StrictMode issues

    // Cleanup timeout on unmount
    return () => {
      clearTimeout(timeoutId)
    }
  }, [sessionId])

  if (!sessionId) {
    return null
  }

  // Show connecting state
  if (isConnecting && events.length === 0) {
    return (
      <div className="bg-dark-card rounded-xl border border-dark-border p-6">
        <div className="flex items-center gap-3">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <p className="text-gray-400 text-sm">Connecting to agent activity stream...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error && events.length === 0) {
    return (
      <div className="bg-dark-card rounded-xl border border-red-500/30 p-6">
        <p className="text-red-400 text-sm">Unable to connect to activity stream</p>
      </div>
    )
  }

  // Don't render if no events yet
  if (events.length === 0) {
    return null
  }

  return (
    <div className="bg-dark-card rounded-xl border border-dark-border p-6 space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white">Agent Activity</h3>
        {isComplete && (
          <span className="text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded">
            Complete
          </span>
        )}
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {events.map((event, idx) => (
          <ActivityEvent key={idx} event={event} />
        ))}
      </div>
    </div>
  )
}

function ActivityEvent({ event }) {
  const {
    type,
    agent,
    action,
    message,
    icon,
    timestamp,
    iteration,
    max_iterations
  } = event

  // Different styles based on event type
  const getEventStyle = () => {
    switch (type) {
      case 'agent_start':
        return 'bg-blue-500/10 border-blue-500/30'
      case 'agent_complete':
        return 'bg-green-500/10 border-green-500/30'
      case 'refinement':
        return 'bg-yellow-500/10 border-yellow-500/30'
      case 'error':
        return 'bg-red-500/10 border-red-500/30'
      case 'iteration_start':
        return 'bg-purple-500/10 border-purple-500/30'
      case 'complete':
        return 'bg-green-500/10 border-green-500/30'
      default:
        return 'bg-dark-surface border-dark-border'
    }
  }

  const getIconColor = () => {
    switch (type) {
      case 'agent_start':
        return 'text-blue-400'
      case 'agent_complete':
        return 'text-green-400'
      case 'refinement':
        return 'text-yellow-400'
      case 'error':
        return 'text-red-400'
      case 'iteration_start':
        return 'text-purple-400'
      case 'complete':
        return 'text-green-400'
      default:
        return 'text-gray-400'
    }
  }

  const formatTime = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // Special rendering for iteration start
  if (type === 'iteration_start') {
    return (
      <div className={`p-3 rounded-lg border ${getEventStyle()} transition-all`}>
        <div className="flex items-center gap-3">
          <span className={`text-2xl ${getIconColor()}`}>{icon}</span>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className="text-white font-semibold">
                Iteration {iteration}/{max_iterations}
              </p>
              <span className="text-xs text-gray-400">{formatTime(timestamp)}</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`p-3 rounded-lg border ${getEventStyle()} transition-all`}>
      <div className="flex items-start gap-3">
        <span className={`text-xl ${getIconColor()}`}>{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              {agent && (
                <p className="text-xs font-semibold text-gray-400">{agent}</p>
              )}
              <p className="text-white font-medium">{action}</p>
              <p className="text-sm text-gray-300 mt-1">{message}</p>
            </div>
            <span className="text-xs text-gray-400 whitespace-nowrap">{formatTime(timestamp)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
