import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'

const AgentActivityLogSSE = ({ sessionId, onComplete }) => {
  const [events, setEvents] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const scrollRef = useRef(null)
  const eventSourceRef = useRef(null)

  useEffect(() => {
    if (!sessionId) {
      console.log('[AgentActivityLogSSE] No sessionId, skipping')
      return
    }

    console.log('[AgentActivityLogSSE] 🚀 Setting up fetch-based SSE for sessionId:', sessionId)

    let abortController = new AbortController()
    let cleanedUp = false

    const connectSSE = async () => {
      try {
        const url = `http://localhost:8000/api/strategy/progress/${sessionId}`
        console.log('[AgentActivityLogSSE] 📡 Connecting to:', url)

        const response = await fetch(url, {
          signal: abortController.signal,
          headers: {
            'Accept': 'text/event-stream',
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        console.log('[AgentActivityLogSSE] ✅ Connection established')
        setError(null)

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (!cleanedUp) {
          const { done, value } = await reader.read()

          if (done) {
            console.log('[AgentActivityLogSSE] Stream ended')
            break
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = line.slice(6) // Remove 'data: ' prefix
                const event = JSON.parse(data)
                console.log('[AgentActivityLogSSE] 📨 Received event:', event)

                // Handle ready signal - notify App that stream is ready
                if (event.type === 'ready') {
                  console.log('[AgentActivityLogSSE] ✅ Stream ready, signaling to App...')
                  if (window.sseStreamReady) {
                    window.sseStreamReady(sessionId)
                  }
                  continue
                }

                // Skip connection acknowledgment
                if (event.type === 'connected') {
                  console.log('[AgentActivityLogSSE] Connected to stream')
                  continue
                }

                // Add event to list
                if (!cleanedUp) {
                  setEvents(prev => [...prev, event])

                  // Check for completion
                  if (event.type === 'complete' || event.type === 'error') {
                    console.log('[AgentActivityLogSSE] 🎉 Workflow complete!')
                    setIsComplete(true)

                    // Notify parent
                    if (onComplete) {
                      console.log('[AgentActivityLogSSE] Notifying parent of completion')
                      onComplete(sessionId)
                    }

                    reader.cancel()
                    return
                  }
                }
              } catch (err) {
                console.error('[AgentActivityLogSSE] ❌ Error parsing event:', err)
              }
            }
          }
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          console.log('[AgentActivityLogSSE] Connection aborted (cleanup)')
        } else {
          console.error('[AgentActivityLogSSE] ❌ Connection error:', err)
          if (!cleanedUp) {
            setError('Connection failed. Please refresh the page.')
          }
        }
      }
    }

    connectSSE()

    // Cleanup
    return () => {
      console.log('[AgentActivityLogSSE] 🧹 Cleaning up SSE connection')
      cleanedUp = true
      abortController.abort()
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

  // Group events by agent phase
  const phases = [
    { key: 'parse', label: 'Parsing Strategy', icon: 'PARSE' },
    { key: 'code', label: 'Generating Code', icon: 'CODE' },
    { key: 'backtest', label: 'Running Backtest', icon: 'TEST' },
    { key: 'analyze', label: 'Analyzing Results', icon: 'ANALYZE' },
    { key: 'refine', label: 'Refining Strategy', icon: 'REFINE' },
  ]

  const getPhaseStatus = (phaseKey) => {
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

AgentActivityLogSSE.propTypes = {
  sessionId: PropTypes.string,
  onComplete: PropTypes.func
}

export default AgentActivityLogSSE
