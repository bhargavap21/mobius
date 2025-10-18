import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Share2, Users, Star, TrendingUp, Eye, Download, Heart, ArrowLeft, Plus, Save, Sparkles } from 'lucide-react'

export default function CommunityPage({ userAgents = [], isAuthenticated = false }) {
  const navigate = useNavigate()
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
      {/* Header */}
      <div className="bg-dark-surface/50 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="text-white/60 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-3xl md:text-4xl font-light text-white leading-tight">Community</h1>
                <p className="mt-1 text-sm text-white/60">Share your trading agents and discover strategies from other traders</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={handleGoCreateAgents}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-accent-600 to-accent-400 text-sm font-medium text-black hover:opacity-95 transition-opacity flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Create Agents
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-8 border border-white/10 bg-transparent p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('shared')}
            className={`px-4 py-2 rounded-md text-sm font-light transition-colors ${
              activeTab === 'shared'
                ? 'bg-accent text-white'
                : 'text-white/60 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            Shared Agents
          </button>
          {isAuthenticated && (
            <button
              onClick={() => setActiveTab('share')}
              className={`px-4 py-2 rounded-md text-sm font-light transition-colors ${
                activeTab === 'share'
                  ? 'bg-accent text-white'
                  : 'text-white/60 hover:text-white'
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
          <div className="bg-transparent rounded-2xl border border-white/10 p-12 text-center">
            <Share2 className="w-16 h-16 text-white/40 mx-auto mb-4" />
            <h3 className="text-xl font-light text-white mb-2">Sign In to Share Agents</h3>
            <p className="text-white/60 mb-6">You need to be signed in to share your trading agents with the community.</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setActiveTab('shared')}
                className="bg-transparent border border-white/20 text-white px-6 py-3 rounded-xl hover:border-accent/40 hover:text-accent transition-colors font-light"
              >
                Browse Community Instead
              </button>
              <button
                onClick={handleGoCreateAgents}
                className="bg-gradient-to-r from-accent-600 to-accent-400 text-black px-6 py-3 rounded-xl hover:opacity-95 transition-opacity font-medium"
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
          <div key={i} className="bg-transparent rounded-2xl border border-white/10 overflow-hidden animate-pulse">
            {/* Image placeholder */}
            <div className="aspect-[16/9] bg-white/5"></div>
            
            {/* Content placeholder */}
            <div className="p-5">
              <div className="h-5 bg-white/10 rounded mb-2"></div>
              <div className="h-3 bg-white/10 rounded mb-1 w-1/3"></div>
              <div className="h-3 bg-white/10 rounded mb-4 w-2/3"></div>
              
              {/* Metrics placeholder */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="border border-white/10 rounded-xl p-3">
                  <div className="h-6 bg-white/10 rounded mb-1"></div>
                  <div className="h-2 bg-white/10 rounded"></div>
                </div>
                <div className="border border-white/10 rounded-xl p-3">
                  <div className="h-6 bg-white/10 rounded mb-1"></div>
                  <div className="h-2 bg-white/10 rounded"></div>
                </div>
              </div>
              
              {/* Tags placeholder */}
              <div className="flex gap-2 mb-4">
                <div className="h-5 bg-white/10 rounded-full w-16"></div>
                <div className="h-5 bg-white/10 rounded-full w-20"></div>
              </div>
              
              {/* Buttons placeholder */}
              <div className="flex gap-3">
                <div className="flex-1 h-10 bg-white/10 rounded-xl"></div>
                <div className="flex-1 h-10 bg-white/10 rounded-xl"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (agents.length === 0) {
    return (
      <div className="bg-transparent rounded-2xl border border-white/10 p-12 text-center">
        <Users className="w-16 h-16 text-white/40 mx-auto mb-4" />
        <h3 className="text-xl font-light text-white mb-2">No Agents Shared Yet</h3>
        <p className="text-white/60 mb-6">Be the first to share a trading agent with the community!</p>
        <button
          onClick={() => window.location.href = '/'}
          className="bg-gradient-to-r from-accent-600 to-accent-400 text-black px-6 py-3 rounded-lg font-medium hover:opacity-95 transition-opacity"
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
    <article className="group relative flex flex-col rounded-2xl border border-white/10 bg-transparent transition hover:border-accent/40 hover:bg-white/5 focus-within:ring-2 focus-within:ring-accent overflow-hidden">
      {/* Placeholder Image */}
      <div className="aspect-[16/9] w-full bg-gradient-to-b from-white/10 to-transparent flex items-center justify-center relative overflow-hidden rounded-t-2xl">
        <div className="text-8xl opacity-80 group-hover:scale-110 transition-transform duration-300">
          {getPlaceholderImage(agent)}
        </div>
        
        {/* Performance Badge */}
        <div className="absolute top-4 right-4">
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
            agent.total_return > 0 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-red-500/20 text-red-400 border border-red-500/30'
          }`}>
            {agent.total_return > 0 ? '+' : ''}{agent.total_return.toFixed(1)}%
          </div>
        </div>

        {/* Symbol Badge */}
        <div className="absolute top-4 left-4">
          <div className="px-3 py-1 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium text-white border border-white/20">
            {agent.symbol}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col gap-3 p-5">
        {/* Header */}
        <div>
          <h3 className="text-lg font-semibold tracking-tight text-white group-hover:text-accent transition-colors mb-1">
            {agent.name}
          </h3>
          <p className="text-xs text-white/60 mb-2">by {agent.author || agent.author_name}</p>
          <p className="text-sm text-white/70 line-clamp-3 leading-relaxed">
            {agent.description}
          </p>
        </div>

        {/* Performance Metrics */}
        <div className="mt-2 grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-white/10 bg-transparent p-3 text-center">
            <div className="text-xl font-semibold text-white">{agent.win_rate}%</div>
            <div className="text-[11px] uppercase tracking-wide text-white/60">Win Rate</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-transparent p-3 text-center">
            <div className="text-xl font-semibold text-white">{agent.total_trades}</div>
            <div className="text-[11px] uppercase tracking-wide text-white/60">Trades</div>
          </div>
        </div>

        {/* Tags */}
        <div className="mt-2 flex flex-wrap gap-2">
          {agent.tags?.slice(0, 3).map((tag, index) => (
            <span key={index} className="rounded-full border border-white/10 bg-transparent px-2 py-0.5 text-xs text-white/60">
              {tag}
            </span>
          ))}
          {agent.tags?.length > 3 && (
            <span className="rounded-full border border-white/10 bg-transparent px-2 py-0.5 text-xs text-white/60">
              +{agent.tags.length - 3}
            </span>
          ))}
        </div>

        {/* Engagement Stats */}
        <div className="flex items-center justify-between text-xs text-white/60 pt-2 border-t border-white/10">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1">
              <Eye className="w-3.5 h-3.5" />
              <span>{agent.views?.toLocaleString() || 0}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Heart className="w-3.5 h-3.5" />
              <span>{agent.likes}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Download className="w-3.5 h-3.5" />
              <span>{agent.downloads}</span>
            </div>
          </div>
          <div>
            {formatDate(agent.shared_at)}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-auto flex flex-col gap-3 pt-3">
          {/* Primary Actions Row */}
          <div className="flex gap-3">
            <button
              onClick={() => onLike(agent.id)}
              className={`flex-1 rounded-xl border transition-colors px-4 py-2 text-sm flex items-center justify-center space-x-2 ${
                agent.liked
                  ? 'border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20'
                  : 'border-white/15 bg-transparent text-white hover:border-accent/40 hover:text-accent'
              }`}
            >
              <Heart className={`w-4 h-4 ${agent.liked ? 'fill-current' : ''}`} />
              <span className="font-light">{agent.liked ? 'Liked' : 'Like'}</span>
            </button>
            <button
              onClick={() => onDownload(agent.id)}
              className="flex-1 rounded-xl bg-gradient-to-r from-accent-600 to-accent-400 px-4 py-2 text-sm font-medium text-black hover:opacity-95 transition-opacity flex items-center justify-center space-x-2"
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
                className="flex-1 py-2 px-4 bg-transparent text-green-400 border border-green-500/30 rounded-xl font-light hover:bg-green-500/10 transition-colors text-sm flex items-center justify-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Save</span>
              </button>
              <button
                onClick={() => onRemix(agent.id)}
                className="flex-1 py-2 px-4 bg-transparent text-purple-400 border border-purple-500/30 rounded-xl font-light hover:bg-purple-500/10 transition-colors text-sm flex items-center justify-center space-x-2"
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
    <div className="bg-transparent rounded-2xl border border-white/10 p-6">
      <h3 className="text-xl font-light text-white mb-6">Share Your Agent</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-light text-white/80 mb-2">
            Select Agent to Share
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="w-full px-3 py-2 bg-transparent border border-white/10 rounded-lg text-white focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent"
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
          <label className="block text-sm font-light text-white/80 mb-2">
            Display Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 bg-transparent border border-white/10 rounded-lg text-white focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent"
            placeholder="Give your agent a catchy name..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-light text-white/80 mb-2">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 bg-transparent border border-white/10 rounded-lg text-white focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent h-24 resize-none"
            placeholder="Describe what makes your agent special..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-light text-white/80 mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="w-full px-3 py-2 bg-transparent border border-white/10 rounded-lg text-white focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent"
            placeholder="momentum, scalping, crypto, etc."
          />
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 bg-transparent border border-white/20 text-white rounded-xl hover:border-accent/40 hover:text-accent transition-colors font-light"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-gradient-to-r from-accent-600 to-accent-400 text-black rounded-xl hover:opacity-95 transition-opacity font-medium"
          >
            Share Agent
          </button>
        </div>
      </form>
    </div>
  )
}
