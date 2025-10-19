import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Share2, Users, Star, TrendingUp, Eye, Download, Heart, ArrowLeft, Plus, Save, Sparkles } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function CommunityPage({ userAgents = [] }) {
  const navigate = useNavigate()
  const { user, isAuthenticated, signout } = useAuth()
  const [activeTab, setActiveTab] = useState('shared')
  const [sharedAgents, setSharedAgents] = useState([])
  const [loading, setLoading] = useState(false)
  const [showShareForm, setShowShareForm] = useState(false)

  // Fetch shared agents from community
  useEffect(() => {
    fetchSharedAgents()
  }, [])

  const fetchSharedAgents = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/community/agents')
      if (response.ok) {
        const data = await response.json()
        setSharedAgents(data.agents)
      } else {
        console.error('Failed to fetch shared agents')
      }
    } catch (error) {
      console.error('Error fetching shared agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleShareAgent = async (agentData) => {
    try {
      const response = await fetch('http://localhost:8000/api/community/share', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      })

      if (response.ok) {
        setShowShareForm(false)
        fetchSharedAgents() // Refresh the list
      }
    } catch (error) {
      console.error('Error sharing agent:', error)
    }
  }

  const handleLikeAgent = async (agentId) => {
    if (!isAuthenticated) {
      alert('Please sign in to like agents')
      return
    }

    try {
      // Optimistically update the UI
      setSharedAgents(prevAgents => 
        prevAgents.map(agent => 
          agent.id === agentId 
            ? { ...agent, liked: !agent.liked }
            : agent
        )
      )

      const response = await fetch(`http://localhost:8000/api/community/agents/${agentId}/like`, {
        method: 'POST',
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Like response:', result.message)
        // Refresh to get the actual state from server
        fetchSharedAgents()
      } else {
        // Revert optimistic update on error
        setSharedAgents(prevAgents => 
          prevAgents.map(agent => 
            agent.id === agentId 
              ? { ...agent, liked: !agent.liked }
              : agent
          )
        )
        console.error('Failed to like agent')
      }
    } catch (error) {
      console.error('Error liking agent:', error)
      // Revert optimistic update on error
      setSharedAgents(prevAgents => 
        prevAgents.map(agent => 
          agent.id === agentId 
            ? { ...agent, liked: !agent.liked }
            : agent
        )
      )
    }
  }

  const handleDownloadAgent = async (agentId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/community/agents/${agentId}/download`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `trading-agent-${agentId}.json`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        // Show success message
        console.log(`✅ Downloaded agent configuration: ${agentId}`)
        
        // Refresh the agents list to update download counts
        fetchSharedAgents()
      } else {
        console.error('Failed to download agent')
        alert('Failed to download agent. Please try again.')
      }
    } catch (error) {
      console.error('Error downloading agent:', error)
      alert('Error downloading agent. Please try again.')
    }
  }

  const handleSaveToMyBots = async (agentId) => {
    if (!isAuthenticated) {
      alert('Please sign in to save agents to your collection')
      return
    }

    try {
      // Get the agent configuration
      const response = await fetch(`http://localhost:8000/api/community/agents/${agentId}/download`)
      if (response.ok) {
        const agentConfig = await response.json()
        
        // Save to user's bot collection
        const saveResponse = await fetch('http://localhost:8000/api/bots', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: `${agentConfig.name} (Saved)`,
            description: `Saved from community: ${agentConfig.description}`,
            strategy_config: agentConfig.strategy,
            backtest_results: agentConfig.backtest_results,
            source: 'community',
            original_agent_id: agentId
          }),
        })

        if (saveResponse.ok) {
          console.log(`✅ Agent saved to My Bots: ${agentId}`)
          alert('Agent saved to your My Bots collection!')
        } else {
          console.error('Failed to save agent')
          alert('Failed to save agent. Please try again.')
        }
      } else {
        console.error('Failed to get agent configuration')
        alert('Failed to get agent configuration. Please try again.')
      }
    } catch (error) {
      console.error('Error saving agent:', error)
      alert('Error saving agent. Please try again.')
    }
  }

  const handleRemixAgent = (agentId) => {
    if (!isAuthenticated) {
      alert('Please sign in to remix agents')
      return
    }

    // Navigate to main page with remix mode
    navigate(`/?remix=${agentId}`)
  }

  const handleGoCreateAgents = () => {
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Navbar */}
      <div className="sticky top-0 z-50 bg-dark-surface/50 backdrop-blur-sm border-b border-dark-border">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-white hover:opacity-80 transition-opacity"
          >
            <span className="text-2xl font-serif italic">Mobius</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-sm font-light rounded-lg border border-white/20 text-white/80 hover:border-accent hover:text-accent transition-colors"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/community')}
              className="px-4 py-2 text-sm font-light rounded-lg border border-accent text-accent transition-colors"
            >
              Community
            </button>

            {isAuthenticated ? (
              <div className="flex items-center gap-2 pl-3 border-l border-gray-700">
                <span className="text-sm text-gray-400">
                  {user?.full_name ? user.full_name.split(' ')[0] : user?.email}
                </span>
                <div className="relative group">
                  <button className="text-sm text-gray-400 hover:text-white p-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </button>

                  <div className="absolute right-0 top-full mt-1 w-32 bg-dark-surface rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="py-1">
                      <button
                        onClick={signout}
                        className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-dark-bg hover:text-red-300 transition-colors"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-100 transition-colors"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-dark-bg border-b border-dark-border">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-semibold text-white mb-2">Community</h1>
              <p className="text-gray-400">Share your trading agents and discover strategies from other traders</p>
            </div>

            <button
              onClick={handleGoCreateAgents}
              className="px-6 py-3 rounded-lg bg-accent text-white hover:bg-accent/90 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Agents
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-8 bg-dark-surface p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('shared')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'shared'
                ? 'bg-accent-primary text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            Shared Agents
          </button>
          {isAuthenticated && (
            <button
              onClick={() => setActiveTab('share')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'share'
                  ? 'bg-accent-primary text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Share2 className="w-4 h-4 inline mr-2" />
              Share Agent
            </button>
          )}
        </div>

        {/* Content */}
        {activeTab === 'shared' && (
          <SharedAgentsList 
            agents={sharedAgents} 
            loading={loading}
            onLike={handleLikeAgent}
            onDownload={handleDownloadAgent}
            onSaveToMyBots={handleSaveToMyBots}
            onRemix={handleRemixAgent}
            isAuthenticated={isAuthenticated}
          />
        )}

        {activeTab === 'share' && !isAuthenticated && (
          <div className="bg-dark-surface rounded-xl border border-dark-border p-8 text-center">
            <Share2 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Sign In to Share Agents</h3>
            <p className="text-gray-400 mb-6">You need to be signed in to share your trading agents with the community.</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setActiveTab('shared')}
                className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Browse Community Instead
              </button>
              <button
                onClick={handleGoCreateAgents}
                className="bg-accent-primary text-white px-6 py-3 rounded-lg hover:bg-accent-primary/90 transition-colors"
              >
                Create Your First Agent
              </button>
            </div>
          </div>
        )}

        {activeTab === 'share' && isAuthenticated && (
          <ShareAgentForm 
            userAgents={userAgents}
            onShare={handleShareAgent}
            onCancel={() => setActiveTab('shared')}
          />
        )}
      </div>
    </div>
  )
}

// Shared Agents List Component
function SharedAgentsList({ agents, loading, onLike, onDownload, onSaveToMyBots, onRemix, isAuthenticated }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="rounded-2xl border border-white/10 bg-transparent overflow-hidden animate-pulse">
            {/* Image placeholder */}
            <div className="h-48 bg-gray-700"></div>
            
            {/* Content placeholder */}
            <div className="p-6">
              <div className="h-6 bg-gray-700 rounded mb-3"></div>
              <div className="h-4 bg-gray-700 rounded mb-2"></div>
              <div className="h-4 bg-gray-700 rounded mb-4 w-3/4"></div>
              
              {/* Metrics placeholder */}
              <div className="grid grid-cols-2 gap-4 mb-4 p-4 bg-gray-800 rounded-lg">
                <div className="text-center">
                  <div className="h-6 bg-gray-700 rounded mb-1"></div>
                  <div className="h-3 bg-gray-700 rounded"></div>
                </div>
                <div className="text-center">
                  <div className="h-6 bg-gray-700 rounded mb-1"></div>
                  <div className="h-3 bg-gray-700 rounded"></div>
                </div>
              </div>
              
              {/* Tags placeholder */}
              <div className="flex gap-2 mb-4">
                <div className="h-6 bg-gray-700 rounded-full w-16"></div>
                <div className="h-6 bg-gray-700 rounded-full w-20"></div>
              </div>
              
              {/* Buttons placeholder */}
              <div className="flex gap-3">
                <div className="flex-1 h-12 bg-gray-700 rounded-lg"></div>
                <div className="flex-1 h-12 bg-gray-700 rounded-lg"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (agents.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-transparent p-8 text-center">
        <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-light text-white mb-2">No Agents Shared Yet</h3>
        <p className="font-light text-gray-400 mb-6">Be the first to share a trading agent with the community!</p>
        <button
          onClick={() => window.location.href = '/'}
          className="bg-accent-primary text-white px-6 py-3 rounded-lg font-light hover:bg-accent-primary/90 transition-colors"
        >
          Create Your First Agent
        </button>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map((agent) => (
        <AgentPlacard 
          key={agent.id} 
          agent={agent} 
          onLike={onLike}
          onDownload={onDownload}
          onSaveToMyBots={onSaveToMyBots}
          onRemix={onRemix}
          isAuthenticated={isAuthenticated}
        />
      ))}
    </div>
  )
}

// Agent Placard Component
function AgentPlacard({ agent, onLike, onDownload, onSaveToMyBots, onRemix, isAuthenticated }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getPerformanceColor = (returnPct) => {
    if (returnPct > 0) return 'text-green-400'
    if (returnPct < 0) return 'text-red-400'
    return 'text-gray-400'
  }

  // Get placeholder image based on agent type/tags
  const getPlaceholderImage = (agent) => {
    const tags = agent.tags || []
    if (tags.some(tag => tag.toLowerCase().includes('elon') || tag.toLowerCase().includes('tweet'))) {
      return '🚀' // Rocket for Elon/Twitter strategies
    } else if (tags.some(tag => tag.toLowerCase().includes('reddit') || tag.toLowerCase().includes('wsb'))) {
      return '📈' // Chart for Reddit strategies
    } else if (tags.some(tag => tag.toLowerCase().includes('rsi') || tag.toLowerCase().includes('technical'))) {
      return '📊' // Bar chart for technical strategies
    } else if (tags.some(tag => tag.toLowerCase().includes('crypto'))) {
      return '₿' // Bitcoin for crypto strategies
    } else if (tags.some(tag => tag.toLowerCase().includes('momentum'))) {
      return '⚡' // Lightning for momentum strategies
    } else {
      return '🤖' // Default robot icon
    }
  }

  return (
    <div className="group relative flex flex-col h-full rounded-2xl border border-white/10 bg-transparent overflow-hidden transition hover:border-accent/40 hover:bg-white/5 focus-within:ring-2 focus-within:ring-accent">
      {/* Content */}
      <div className="p-6 flex flex-col h-full">
        {/* Header */}
        <div className="mb-4 flex-shrink-0">
          <div className="flex items-start justify-between gap-3 mb-2 min-h-[56px]">
            <h3 className="text-base font-light tracking-tight text-white group-hover:text-accent-primary transition-colors flex-1 leading-snug">
              {agent.name}
            </h3>
            <div className={`px-3 py-1 rounded-full text-sm font-light whitespace-nowrap flex-shrink-0 self-start ${
              agent.total_return > 0 
                ? 'bg-transparent text-green-400 border border-green-500/30' 
                : 'bg-transparent text-red-400 border border-red-500/30'
            }`}>
              {agent.total_return > 0 ? '+' : ''}{agent.total_return.toFixed(1)}%
            </div>
          </div>
          <div className="flex items-center gap-2 mb-3">
            <span className="px-3 py-1 bg-transparent rounded-full text-sm font-light text-white border border-white/20 flex-shrink-0">
              {agent.symbol}
            </span>
            <span className="text-sm font-light text-gray-400">
              by {agent.author || agent.author_name}
            </span>
          </div>
          <p className="text-sm font-light text-gray-300 leading-relaxed min-h-[60px]">
            {agent.description}
          </p>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-4 p-4 bg-transparent border border-white/10 rounded-lg flex-shrink-0">
          <div className="text-center">
            <div className="text-lg font-light text-white">{agent.win_rate}%</div>
            <div className="text-xs font-light text-gray-400">Win Rate</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-light text-white">{agent.total_trades}</div>
            <div className="text-xs font-light text-gray-400">Trades</div>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4 flex-shrink-0">
          {agent.tags?.slice(0, 3).map((tag, index) => (
            <span key={index} className="px-3 py-1 bg-accent-primary/20 text-accent-primary text-xs rounded-full font-light">
              {tag}
            </span>
          ))}
          {agent.tags?.length > 3 && (
            <span className="px-3 py-1 bg-gray-700/50 text-gray-300 text-xs rounded-full font-light">
              +{agent.tags.length - 3}
            </span>
          )}
        </div>

        {/* Engagement Stats */}
        <div className="flex items-center justify-between mb-4 text-sm font-light text-gray-400 flex-shrink-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <Eye className="w-4 h-4" />
              <span>{agent.views?.toLocaleString() || 0}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Heart className="w-4 h-4" />
              <span>{agent.likes}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Download className="w-4 h-4" />
              <span>{agent.downloads}</span>
            </div>
          </div>
          <div className="text-xs font-light">
            {formatDate(agent.shared_at)}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3 mt-auto">
          {/* Primary Actions Row */}
          <div className="flex gap-3">
            <button
              onClick={() => onLike(agent.id)}
              className={`flex-1 py-3 px-4 rounded-lg font-light transition-all duration-200 flex items-center justify-center space-x-2 ${
                agent.liked
                  ? 'bg-transparent text-red-400 border border-red-500/30 hover:bg-red-500/10'
                  : 'bg-transparent text-gray-300 border border-white/20 hover:border-accent/40 hover:text-white'
              }`}
            >
              <Heart className={`w-4 h-4 ${agent.liked ? 'fill-current' : ''}`} />
              <span>{agent.liked ? 'Liked' : 'Like'}</span>
            </button>
            <button
              onClick={() => onDownload(agent.id)}
              className="flex-1 py-3 px-4 bg-transparent text-accent border border-accent/30 rounded-lg font-light hover:bg-accent/10 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>

          {/* Secondary Actions Row - Only show for authenticated users */}
          {isAuthenticated && (
            <div className="flex gap-3">
              <button
                onClick={() => onSaveToMyBots(agent.id)}
                className="flex-1 py-2 px-4 bg-transparent text-green-400 border border-green-500/30 rounded-lg font-light hover:bg-green-500/10 transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Save</span>
              </button>
              <button
                onClick={() => onRemix(agent.id)}
                className="flex-1 py-2 px-4 bg-transparent text-purple-400 border border-purple-500/30 rounded-lg font-light hover:bg-purple-500/10 transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Remix</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Share Agent Form Component
function ShareAgentForm({ userAgents, onShare, onCancel }) {
  const [selectedAgent, setSelectedAgent] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!selectedAgent || !name || !description) return

    const agentData = {
      original_bot_id: selectedAgent,
      name,
      description,
      tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
    }

    onShare(agentData)
  }

  return (
    <div className="bg-dark-surface rounded-xl border border-dark-border p-6">
      <h3 className="text-xl font-semibold text-white mb-6">Share Your Agent</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Agent to Share
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-accent-primary"
            required
          >
            <option value="">Choose an agent...</option>
            {userAgents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} - {agent.description}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Display Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-accent-primary"
            placeholder="Give your agent a catchy name..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-accent-primary h-24 resize-none"
            placeholder="Describe what makes your agent special..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-accent-primary"
            placeholder="momentum, scalping, crypto, etc."
          />
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-colors"
          >
            Share Agent
          </button>
        </div>
      </form>
    </div>
  )
}
