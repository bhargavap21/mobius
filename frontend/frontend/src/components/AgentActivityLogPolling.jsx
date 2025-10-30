import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'

const AgentActivityLogPolling = ({ sessionId, onComplete }) => {
  const [events, setEvents] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const scrollRef = useRef(null)
  const eventIndexRef = useRef(0) // Use ref to persist across renders
  const retryCountRef = useRef(0) // Track retry attempts
  const maxRetries = 3 // Maximum retry attempts
  const circuitBreakerRef = useRef(false) // Circuit breaker to temporarily stop polling
  const effectInstanceRef = useRef(0) // Track effect instances for debugging
  const activeIntervalRef = useRef(null) // Track the active interval ID

  useEffect(() => {
    if (!sessionId) {
      console.log('[AgentActivityLogPolling] No sessionId, skipping polling setup')
      return
    }

    // Generate unique ID for this effect instance
    const effectInstanceId = ++effectInstanceRef.current
    console.log(`[AgentActivityLogPolling] 🚀 Effect #${effectInstanceId} STARTED for sessionId: ${sessionId}`)

    // CRITICAL: Use local variable for polling flag instead of shared ref
    // This prevents race conditions between multiple effect instances (React StrictMode)
    let isPollingThisInstance = false
    let intervalId = null
    let cleanedUp = false

    // Reset state for new session
    eventIndexRef.current = 0
    retryCountRef.current = 0
    circuitBreakerRef.current = false

    const pollForEvents = async () => {
      // Check if this effect has been cleaned up
      if (cleanedUp) {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Skipping poll (cleaned up)`)
        return
      }

      // Check circuit breaker
      if (circuitBreakerRef.current) {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Circuit breaker open, skipping request`)
        return
      }

      // Prevent concurrent requests FOR THIS INSTANCE
      if (isPollingThisInstance) {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - ⚠️ Request already in progress for this instance, skipping...`)
        return
      }

      console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - 🔄 Starting poll request`)
      isPollingThisInstance = true
      console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Set isPollingThisInstance = true`)

      try {
        const url = `http://localhost:8000/api/strategy/events/${sessionId}?from=${eventIndexRef.current}`
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - 📡 Polling: ${url}`)

        const response = await fetch(url)
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Response status: ${response.status}`)

        if (!response.ok) {
          if (response.status === 404) {
            console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Session not found yet (404), will retry...`)
            return // Early return - flag will be reset in finally block
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Reset retry counter on successful request
        retryCountRef.current = 0
        setError(null)

        const data = await response.json()
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Poll response:`, data)

        if (data.events && data.events.length > 0) {
          console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - ✅ Received ${data.events.length} new events`)

          // Only update state if still not cleaned up
          if (!cleanedUp) {
            setEvents(prev => [...prev, ...data.events])
            eventIndexRef.current += data.events.length

            // Check for completion
            const lastEvent = data.events[data.events.length - 1]
            if (lastEvent.type === 'complete' || lastEvent.type === 'error') {
              console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - 🎉 Workflow complete!`)
              setIsComplete(true)

              if (intervalId) {
                console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Clearing interval`)
                clearInterval(intervalId)
                intervalId = null
              }

              // Notify parent component that workflow is complete
              if (onComplete) {
                console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Notifying parent of completion`)
                onComplete(sessionId)
              }
            }
          }
        } else {
          console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - No new events`)
        }
      } catch (error) {
        retryCountRef.current += 1
        console.error(`[AgentActivityLogPolling] Effect #${effectInstanceId} - ❌ Error polling:`, error, `(attempt ${retryCountRef.current}/${maxRetries})`)

        if (retryCountRef.current >= maxRetries) {
          setError(`Failed to connect after ${maxRetries} attempts. Please refresh the page.`)
          console.error(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Max retries exceeded, opening circuit breaker`)
          circuitBreakerRef.current = true

          // Reset circuit breaker after 30 seconds
          setTimeout(() => {
            if (!cleanedUp) {
              circuitBreakerRef.current = false
              retryCountRef.current = 0
              console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Circuit breaker reset`)
            }
          }, 30000)

          return // Early return - flag will be reset in finally block
        }

        setError(null)
      } finally {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - 🔓 Resetting isPollingThisInstance to false (in finally block)`)
        isPollingThisInstance = false
      }
    }

    // Start polling immediately and then set up interval
    const startPolling = async () => {
      console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Starting initial poll...`)
      await pollForEvents()

      // Only set up interval if not cleaned up
      if (!cleanedUp) {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Setting up interval (2000ms)`)
        intervalId = setInterval(pollForEvents, 2000)
        activeIntervalRef.current = intervalId
      } else {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Not setting up interval (cleaned up)`)
      }
    }

    startPolling()

    // Cleanup function
    return () => {
      console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - 🧹 CLEANUP RUNNING`)
      cleanedUp = true

      if (intervalId) {
        console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - Clearing interval in cleanup`)
        clearInterval(intervalId)
        intervalId = null
      }

      console.log(`[AgentActivityLogPolling] Effect #${effectInstanceId} - 🧹 CLEANUP COMPLETE`)
    }
  }, [sessionId]) // Removed onComplete from dependencies - it doesn't need to trigger re-polling

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

  const getEventIcon = (type) => {
    switch (type) {
      case 'agent_start':
        return 'START'
      case 'agent_complete':
        return 'DONE'
      case 'iteration_start':
        return 'ITER'
      case 'refinement':
        return 'REFINE'
      case 'complete':
        return 'SUCCESS'
      case 'error':
        return 'ERROR'
      default:
        return 'LOG'
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

  // Group events by agent phase
  const phases = [
    { key: 'parse', label: 'Parsing Strategy', icon: 'PARSE' },
    { key: 'code', label: 'Generating Code', icon: 'CODE' },
    { key: 'backtest', label: 'Running Backtest', icon: 'TEST' },
    { key: 'analyze', label: 'Analyzing Results', icon: 'ANALYZE' },
    { key: 'refine', label: 'Refining Strategy', icon: 'REFINE' },
  ]

  const getPhaseStatus = (phaseKey) => {
    // Check if this phase has any events
    const phaseEvents = events.filter(e =>
      e.agent?.toLowerCase().includes(phaseKey) ||
      e.message?.toLowerCase().includes(phaseKey) ||
      (phaseKey === 'parse' && e.type === 'agent_start' && e.agent === 'StrategyParser') ||
      (phaseKey === 'code' && e.agent === 'CodeGenerator') ||
      (phaseKey === 'backtest' && e.agent === 'BacktestRunner') ||
      (phaseKey === 'analyze' && e.agent === 'StrategyAnalyst')
    )

    if (phaseEvents.length === 0) return 'pending'

    const lastEvent = phaseEvents[phaseEvents.length - 1]
    if (lastEvent.type === 'agent_complete') return 'done'
    return 'active'
  }

  return (
    <div className="w-full">
      {/* Phase Status Boxes */}
      <div className="space-y-3 mb-6">
        {phases.map((phase, idx) => {
          const status = getPhaseStatus(phase.key)
          const isActive = status === 'active'
          const isDone = status === 'done'
          const isPending = status === 'pending'

          return (
            <div
              key={phase.key}
              className={`flex items-center gap-3 p-4 rounded-lg transition-all duration-500 ${
                isActive
                  ? 'bg-accent-primary/10 border-2 border-accent-primary/30 scale-105'
                  : isDone
                  ? 'bg-green-500/5 border border-green-500/20'
                  : 'bg-dark-surface border border-dark-border opacity-40'
              }`}
            >
              <div
                className={`text-sm font-mono font-semibold transition-transform duration-500 ${
                  isActive ? 'scale-125' : 'scale-100'
                } ${isDone ? 'text-green-400' : isActive ? 'text-accent-primary' : 'text-gray-500'}`}
              >
                {isDone ? 'DONE' : phase.icon}
              </div>
              <div className="flex-1">
                <p className={`font-light text-base ${isActive ? 'text-white' : 'text-gray-400'}`}>
                  {phase.label}
                </p>
              </div>
              {isActive && (
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/30 mb-4">
          <p className="text-red-400 text-sm">⚠️ {error}</p>
        </div>
      )}

      {/* Detailed Event Log */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="space-y-1 max-h-48 overflow-y-auto scroll-smooth bg-dark-surface rounded-lg p-4 border border-dark-border"
      >
        <p className="text-xs text-gray-500 mb-2 font-semibold">ACTIVITY LOG</p>
        {events.length === 0 ? (
          <div className="flex items-center space-x-2 text-gray-400 py-2">
            <div className="animate-spin h-3 w-3 border-2 border-accent-primary border-t-transparent rounded-full"></div>
            <span className="text-xs">Waiting for agent activity...</span>
          </div>
        ) : (
          events.map((event, index) => (
            <div
              key={index}
              className="flex items-start space-x-2 text-xs animate-fadeIn"
            >
              <span className="text-gray-600 mt-0.5">›</span>
              <span className={getEventColor(event.type)}>
                {event.agent || event.type}:
              </span>
              <span className="text-gray-400">{event.message}</span>
            </div>
          ))
        )}
        {isComplete && (
          <div className="pt-2 mt-2 border-t border-dark-border">
            <span className="text-green-400 font-semibold text-sm">
              ✓ Workflow complete!
            </span>
          </div>
        )}
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          This may take 30-60 seconds for complex strategies
        </p>
      </div>
    </div>
  )
}

AgentActivityLogPolling.propTypes = {
  sessionId: PropTypes.string,
  onComplete: PropTypes.func
}

export default AgentActivityLogPolling