import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'

const ClarificationChat = ({ initialQuery, onComplete }) => {
  const [messages, setMessages] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [userInput, setUserInput] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Start clarification flow when component mounts
  useEffect(() => {
    if (initialQuery) {
      startClarification(initialQuery)
    }
  }, [initialQuery])

  // Start clarification flow
  const startClarification = async (query) => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/strategy/clarify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          conversation_history: []
        })
      })

      const data = await response.json()

      if (data.needs_clarification) {
        setCurrentQuestion(data.question)
        setMessages([{ role: 'assistant', content: data.question }])
      } else {
        // No clarification needed, proceed directly
        setIsComplete(true)
        onComplete(data.enriched_query, data.parameters || {})
      }
    } catch (error) {
      console.error('Error getting clarification:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Handle user answer
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!userInput.trim()) return

    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userInput }]
    setMessages(newMessages)
    setUserInput('')
    setIsLoading(true)

    // Get next question or complete
    try {
      // CRITICAL: Prepend the original query to conversation history
      // so the backend knows what the user originally requested
      const conversationWithContext = [
        { role: 'user', content: `Original query: ${initialQuery}` },
        ...newMessages
      ]

      const response = await fetch('http://localhost:8000/api/strategy/clarify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_history: conversationWithContext
        })
      })

      const data = await response.json()

      if (data.needs_clarification) {
        setCurrentQuestion(data.question)
        setMessages([...newMessages, { role: 'assistant', content: data.question }])
      } else {
        // All questions answered, proceed to generation
        setIsComplete(true)
        onComplete(data.enriched_query, data.parameters || {})
      }
    } catch (error) {
      console.error('Error getting next question:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isComplete) {
    return (
      <div className="w-full max-w-4xl mx-auto px-4">
        <div className="bg-white/5 border border-line rounded-xl p-6">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p className="text-fg font-medium">All set! Generating your strategy...</p>
              <p className="text-fg-muted text-sm mt-1">This will take about 1-2 minutes</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-5xl mx-auto px-4 flex flex-col h-[600px]">
      {/* Header */}
      <div className="mb-6 text-center">
        <h3 className="text-2xl font-semibold text-fg mb-2">Let's clarify your strategy</h3>
        <p className="text-fg-muted text-sm">Answer a few quick questions to optimize your trading bot</p>
      </div>

      {/* Chat messages - ChatGPT style */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex gap-3 max-w-3xl items-start ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              {/* Avatar */}
              <div className="flex-shrink-0 mt-1">
                {msg.role === 'assistant' ? (
                  <div className="w-8 h-8 rounded-full bg-accent-dark flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                    <svg className="w-5 h-5 text-fg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                )}
              </div>

              {/* Message bubble */}
              <div
                className={`rounded-xl px-5 py-4 ${
                  msg.role === 'assistant'
                    ? 'bg-white/5 border border-line text-fg'
                    : 'bg-accent-dark text-white'
                }`}
              >
                <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-3 max-w-3xl">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-accent-dark flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
              </div>
              <div className="bg-white/5 border border-line rounded-xl px-5 py-4">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-fg-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-fg-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-fg-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input form - Fixed at bottom */}
      {currentQuestion && !isLoading && (
        <div className="border-t border-line pt-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Type your answer..."
              className="flex-1 px-4 py-3 bg-white/5 border border-line rounded-xl text-fg placeholder:text-fg-muted focus:outline-none focus:ring-2 focus:ring-accent-400"
              autoFocus
            />
            <button
              type="submit"
              disabled={!userInput.trim()}
              className="px-6 py-3 bg-accent-dark text-white rounded-xl hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

ClarificationChat.propTypes = {
  initialQuery: PropTypes.string.isRequired,
  onComplete: PropTypes.func.isRequired
}

export default ClarificationChat
