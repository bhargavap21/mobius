import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

const AgentActivityLogPolling = ({ sessionId, onComplete }) => {
  const [events, setEvents] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!sessionId) return

    let intervalId
    let eventIndex = 0

    const pollForEvents = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/strategy/events/${sessionId}?from=${eventIndex}`)

        if (!response.ok) {
          if (response.status === 404) {
            // Session not found yet, keep polling
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()

        if (data.events && data.events.length > 0) {
          console.log('[AgentActivityLogPolling] Received events:', data.events)
          setEvents(prev => [...prev, ...data.events])
          eventIndex += data.events.length

          // Check for completion
          const lastEvent = data.events[data.events.length - 1]
          if (lastEvent.type === 'complete' || lastEvent.type === 'error') {
            setIsComplete(true)
            if (intervalId) {
              clearInterval(intervalId)
            }

            // Notify parent component that workflow is complete
            if (onComplete) {
              console.log('[AgentActivityLogPolling] Workflow complete, notifying parent...')
              onComplete(sessionId)
            }
          }
        }
      } catch (error) {
        console.error('[AgentActivityLogPolling] Error polling for events:', error)
        setError(error.message)
      }
    }

    // Start polling immediately
    pollForEvents()

    // Poll every second
    intervalId = setInterval(pollForEvents, 1000)

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [sessionId, onComplete])

  if (!sessionId) {
    return null
  }

  if (error) {
    return (
      <div className="p-4 bg-red-500/10 rounded-lg">
        <p className="text-red-400">Error: {error}</p>
      </div>
    )
  }

  if (events.length === 0) {
    return (
      <div className="flex items-center space-x-2 text-gray-400">
        <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        <span>Waiting for agent activity...</span>
      </div>
    )
  }

  const getEventIcon = (type) => {
    switch (type) {
      case 'agent_start':
        return '🤖'
      case 'agent_complete':
        return '✅'
      case 'iteration_start':
        return '🔄'
      case 'refinement':
        return '🔧'
      case 'complete':
        return '🎉'
      case 'error':
        return '❌'
      default:
        return '📝'
    }
  }

  const getEventColor = (type) => {
    switch (type) {
      case 'agent_start':
        return 'text-blue-400'
      case 'agent_complete':
        return 'text-green-400'
      case 'iteration_start':
        return 'text-purple-400'
      case 'refinement':
        return 'text-yellow-400'
      case 'complete':
        return 'text-green-500'
      case 'error':
        return 'text-red-500'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {events.map((event, index) => (
        <div
          key={index}
          className="flex items-start space-x-2 text-sm animate-fadeIn"
        >
          <span className="text-lg">{getEventIcon(event.type)}</span>
          <span className="text-gray-500 mt-0.5">›</span>
          <span className={getEventColor(event.type)}>
            {event.agent || event.type}:
          </span>
          <span className="text-gray-300">{event.message}</span>
        </div>
      ))}
      {isComplete && (
        <div className="pt-2 mt-2 border-t border-gray-700">
          <span className="text-green-400 font-semibold">
            ✨ Workflow complete!
          </span>
        </div>
      )}
    </div>
  )
}

AgentActivityLogPolling.propTypes = {
  sessionId: PropTypes.string,
  onComplete: PropTypes.func
}

export default AgentActivityLogPolling