import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { WS_URL } from '../config'

const AgentActivityLogWS = ({ sessionId, onComplete }) => {
  const [events, setEvents] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const [reconnecting, setReconnecting] = useState(false)
  const scrollRef = useRef(null)
  const wsRef = useRef(null)
  const isCompleteRef = useRef(false) // Track completion with ref for immediate access
  const reconnectAttemptRef = useRef(0) // Track reconnect attempts
  const reconnectTimeoutRef = useRef(null) // Store reconnect timeout

  const MAX_RECONNECT_ATTEMPTS = 5
  const INITIAL_RECONNECT_DELAY = 1000 // 1 second
  const MAX_RECONNECT_DELAY = 30000 // 30 seconds

  useEffect(() => {
    if (!sessionId) {
      console.log('[AgentActivityLogWS] No sessionId, skipping')
      return
    }

    console.log('[AgentActivityLogWS] 🚀 Setting up WebSocket for sessionId:', sessionId)

    let cleanedUp = false

    const reconnectWithBackoff = (attempt = 0) => {
      if (cleanedUp || isCompleteRef.current) {
        return
      }

      if (attempt >= MAX_RECONNECT_ATTEMPTS) {
        console.error('[AgentActivityLogWS] ❌ Max reconnect attempts reached')
        setError('Failed to reconnect after multiple attempts. Please refresh the page.')
        setReconnecting(false)
        return
      }

      // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 30s
      const delay = Math.min(INITIAL_RECONNECT_DELAY * Math.pow(2, attempt), MAX_RECONNECT_DELAY)
      
      console.log(`[AgentActivityLogWS] 🔄 Scheduling reconnect attempt ${attempt + 1} in ${delay}ms...`)
      setReconnecting(true)
      setError(`Reconnecting... (attempt ${attempt + 1}/${MAX_RECONNECT_ATTEMPTS})`)

      reconnectTimeoutRef.current = setTimeout(() => {
        if (!cleanedUp && !isCompleteRef.current) {
          console.log(`[AgentActivityLogWS] 🔄 Reconnecting (attempt ${attempt + 1})...`)
          reconnectAttemptRef.current = attempt + 1
          connectWS()
        }
      }, delay)
    }

    const connectWS = () => {
      const wsUrl = `${WS_URL}/ws/strategy/progress/${sessionId}`
      console.log('[AgentActivityLogWS] 🔌 Connecting to:', wsUrl)

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[AgentActivityLogWS] ✅ WebSocket connection established')
        setError(null)
        setReconnecting(false)
        reconnectAttemptRef.current = 0 // Reset reconnect attempts on successful connection
        // Clear any pending reconnect timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('[AgentActivityLogWS] 📨 Received event:', data)

          // Handle ready signal - notify App that stream is ready
          if (data.type === 'ready') {
            console.log('[AgentActivityLogWS] ✅ Stream ready, signaling to App...')
            if (window.wsStreamReady) {
              window.wsStreamReady(sessionId)
            }
            return
          }

          // Skip heartbeat events
          if (data.type === 'heartbeat') {
            console.log('[AgentActivityLogWS] 💓 Heartbeat received')
            return
          }

          // Add event to list
          if (!cleanedUp) {
            setEvents(prev => [...prev, data])

            // Check for completion
            if (data.type === 'complete' || data.type === 'error') {
              console.log('[AgentActivityLogWS] 🎉 Workflow complete!')
              setIsComplete(true)
              isCompleteRef.current = true // Set ref immediately for onclose handler
              setReconnecting(false)
              
              // Clear any pending reconnect timeout
              if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
                reconnectTimeoutRef.current = null
              }

              // Notify parent
              if (onComplete) {
                console.log('[AgentActivityLogWS] Notifying parent of completion')
                onComplete(sessionId)
              }
            }
          }
        } catch (err) {
          console.error('[AgentActivityLogWS] ❌ Error parsing message:', err)
        }
      }

      ws.onerror = (err) => {
        console.error('[AgentActivityLogWS] ❌ WebSocket error:', err)
        // Don't set error here - onclose will handle reconnection
      }

      ws.onclose = (event) => {
        console.log('[AgentActivityLogWS] 🔌 WebSocket connection closed', { code: event.code, reason: event.reason })
        
        // Use ref instead of state to avoid race condition with async state updates
        if (!cleanedUp && !isCompleteRef.current) {
          // Don't reconnect if it was a normal closure (code 1000) or if we're already reconnecting
          if (event.code !== 1000 && reconnectAttemptRef.current < MAX_RECONNECT_ATTEMPTS) {
            reconnectWithBackoff(reconnectAttemptRef.current)
          } else if (event.code === 1000) {
            // Normal closure - don't show error
            console.log('[AgentActivityLogWS] Normal closure, not reconnecting')
          } else {
            setError('Connection closed unexpectedly.')
          }
        }
      }
    }

    connectWS()

    // Cleanup
    return () => {
      console.log('[AgentActivityLogWS] 🧹 Cleaning up WebSocket connection')
      cleanedUp = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [sessionId]) // Removed onComplete from deps to prevent re-running

  // Detect when user manually scrolls
  const handleScroll = () => {
    if (!scrollRef.current) return

    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 10

    setAutoScroll(isAtBottom)
  }

  // Auto-scroll to bottom when new events arrive
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

  // Map phases to actual agents in the workflow
  const phases = [
    { key: 'supervisor', label: 'Analyzing Strategy', icon: 'PARSE', agent: 'Supervisor' },
    { key: 'insights', label: 'Planning Visualizations', icon: 'CHART', agent: 'InsightsGenerator' },
    { key: 'code', label: 'Generating Code', icon: 'CODE', agent: 'CodeGenerator' },
    { key: 'backtest', label: 'Running Backtest', icon: 'TEST', agent: 'BacktestRunner' },
    { key: 'analyze', label: 'Analyzing Results', icon: 'ANALYZE', agent: 'StrategyAnalyst' },
  ]

  const getPhaseStatus = (phase) => {
    // Find all events for this specific agent
    const phaseEvents = events.filter(e => e.agent === phase.agent)

    if (phaseEvents.length === 0) return 'pending'

    // Check the last event for this agent
    const lastEvent = phaseEvents[phaseEvents.length - 1]

    // Special handling for workflow completion
    const workflowComplete = events.some(e => e.type === 'complete' || e.type === 'error')

    // If workflow is complete, ALL agents that ran at least once should show as done
    if (workflowComplete && phaseEvents.length > 0) {
      return 'done'
    }

    // If last event is agent_complete, phase is done (for current iteration)
    if (lastEvent.type === 'agent_complete') {
      // Check if there's an iteration_start after this complete
      // (which would mean we're starting a new iteration and this agent will run again)
      const lastCompleteIndex = events.lastIndexOf(lastEvent)
      const hasIterationAfter = events.slice(lastCompleteIndex).some(e => e.type === 'iteration_start')

      // If new iteration started, this phase might become active again
      return hasIterationAfter ? 'done' : 'done'
    }

    // If last event is agent_start, phase is active
    if (lastEvent.type === 'agent_start') return 'active'

    return 'pending'
  }

  return (
    <div className="w-full">
      {/* Phase Status Boxes */}
      <div className="space-y-3 mb-6">
        {phases.map((phase, idx) => {
          const status = getPhaseStatus(phase)
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
        <div className={`p-4 rounded-lg border mb-4 ${
          reconnecting 
            ? 'bg-yellow-500/10 border-yellow-500/30' 
            : 'bg-red-500/10 border-red-500/30'
        }`}>
          <p className={`text-sm ${reconnecting ? 'text-yellow-400' : 'text-red-400'}`}>
            {reconnecting ? '🔄' : '⚠️'} {error}
          </p>
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

AgentActivityLogWS.propTypes = {
  sessionId: PropTypes.string,
  onComplete: PropTypes.func
}

export default AgentActivityLogWS
