import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'

const AgentActivityLogPolling = ({ sessionId, onComplete }) => {
  const [events, setEvents] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const scrollRef = useRef(null)
  const eventIndexRef = useRef(0) // Use ref to persist across renders
  const abortControllerRef = useRef(null) // Add abort controller for request cancellation
  const isPollingRef = useRef(false) // Prevent concurrent requests
  const retryCountRef = useRef(0) // Track retry attempts
  const maxRetries = 3 // Maximum retry attempts
  const circuitBreakerRef = useRef(false) // Circuit breaker to temporarily stop polling

  useEffect(() => {
    if (!sessionId) return

    let intervalId
    eventIndexRef.current = 0 // Reset for new session
    retryCountRef.current = 0 // Reset retry counter for new session
    circuitBreakerRef.current = false // Reset circuit breaker for new session

    const pollForEvents = async () => {
      // Check circuit breaker
      if (circuitBreakerRef.current) {
        console.log('[AgentActivityLogPolling] Circuit breaker open, skipping request')
        return
      }

      // Prevent concurrent requests
      if (isPollingRef.current) {
        console.log('[AgentActivityLogPolling] Request already in progress, skipping...')
        return
      }

      isPollingRef.current = true

      try {
        // Cancel any existing request
        if (abortControllerRef.current) {
          abortControllerRef.current.abort()
        }

        // Create new abort controller
        abortControllerRef.current = new AbortController()

        const url = `http://localhost:8000/api/strategy/events/${sessionId}?from=${eventIndexRef.current}`
        console.log('[AgentActivityLogPolling] Polling:', url, 'from index:', eventIndexRef.current)
        
        const response = await fetch(url, {
          signal: abortControllerRef.current.signal,
          timeout: 5000 // 5 second timeout
        })

        if (!response.ok) {
          if (response.status === 404) {
            console.log('[AgentActivityLogPolling] Session not found yet (404), will retry...')
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        console.log('[AgentActivityLogPolling] Poll response:', data)

        // Reset retry counter on successful request
        retryCountRef.current = 0
        setError(null)

        if (data.events && data.events.length > 0) {
          console.log('[AgentActivityLogPolling] Received', data.events.length, 'new events')
          setEvents(prev => [...prev, ...data.events])
          eventIndexRef.current += data.events.length

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
        if (error.name === 'AbortError') {
          console.log('[AgentActivityLogPolling] Request aborted')
          return
        }
        
        retryCountRef.current += 1
        console.error('[AgentActivityLogPolling] Error polling for events:', error, `(attempt ${retryCountRef.current}/${maxRetries})`)
        
        if (retryCountRef.current >= maxRetries) {
          setError(`Failed to connect after ${maxRetries} attempts. Please refresh the page.`)
          console.error('[AgentActivityLogPolling] Max retries exceeded, opening circuit breaker')
          circuitBreakerRef.current = true
          
          // Reset circuit breaker after 30 seconds
          setTimeout(() => {
            circuitBreakerRef.current = false
            retryCountRef.current = 0
            console.log('[AgentActivityLogPolling] Circuit breaker reset, resuming polling')
          }, 30000)
          
          return
        }
        
        // Reset error after successful retry
        setError(null)
      } finally {
        isPollingRef.current = false
      }
    }

    // Start polling immediately
    pollForEvents()

    // Poll every 2000ms (2 seconds) to prevent resource exhaustion
    intervalId = setInterval(pollForEvents, 2000)

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
      // Cancel any pending requests on cleanup
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [sessionId, onComplete])

  // Detect when user manually scrolls
  const handleScroll = () => {
    if (!scrollRef.current) return

    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 10 // 10px threshold

    // If user scrolled up, disable auto-scroll
    // If user scrolled back to bottom, re-enable auto-scroll
    setAutoScroll(isAtBottom)
  }

  // Auto-scroll to bottom when new events arrive (only if auto-scroll is enabled)
  useEffect(() => {
    if (scrollRef.current && autoScroll) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [events.length, autoScroll])

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
    <div
      ref={scrollRef}
      onScroll={handleScroll}
      className="space-y-2 max-h-64 overflow-y-auto scroll-smooth"
    >
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