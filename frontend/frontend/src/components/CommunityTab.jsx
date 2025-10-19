import React, { useState, useEffect } from 'react'
import { Share2, Users, Star, TrendingUp, Eye, Download, Heart } from 'lucide-react'

export default function CommunityTab({ userAgents = [] }) {
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
      const response = await fetch('/api/community/agents')
      if (response.ok) {
        const data = await response.json()
        setSharedAgents(data.agents || [])
      }
    } catch (error) {
      console.error('Error fetching shared agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleShareAgent = async (agentData) => {
    try {
      const response = await fetch('/api/community/share', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Agent shared successfully:', result)
        setShowShareForm(false)
        fetchSharedAgents() // Refresh the list
      }
    } catch (error) {
      console.error('Error sharing agent:', error)
    }
  }

  const handleLikeAgent = async (agentId) => {
    try {
      const response = await fetch(`/api/community/agents/${agentId}/like`, {
        method: 'POST',
      })

      if (response.ok) {
        fetchSharedAgents() // Refresh to show updated likes
      }
    } catch (error) {
      console.error('Error liking agent:', error)
    }
  }

  const handleDownloadAgent = async (agentId) => {
    try {
      const response = await fetch(`/api/community/agents/${agentId}/download`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `agent-${agentId}.json`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error downloading agent:', error)
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Community</h1>
          <p className="text-gray-400">Share your trading agents and discover strategies from other traders</p>
        </div>

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
        </div>

        {/* Content */}
        {activeTab === 'shared' && (
          <SharedAgentsList 
            agents={sharedAgents} 
            loading={loading}
            onLike={handleLikeAgent}
            onDownload={handleDownloadAgent}
          />
        )}

        {activeTab === 'share' && (
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

function SharedAgentsList({ agents, loading, onLike, onDownload }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-dark-surface rounded-xl border border-dark-border p-6 animate-pulse">
            <div className="h-4 bg-gray-700 rounded mb-3"></div>
            <div className="h-3 bg-gray-700 rounded mb-2"></div>
            <div className="h-3 bg-gray-700 rounded mb-4"></div>
            <div className="flex justify-between items-center">
              <div className="h-3 bg-gray-700 rounded w-16"></div>
              <div className="h-3 bg-gray-700 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (agents.length === 0) {
    return (
      <div className="text-center py-12">
        <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">No Shared Agents Yet</h3>
        <p className="text-gray-400 mb-6">Be the first to share your trading agent with the community!</p>
        <button className="bg-accent-primary text-white px-6 py-3 rounded-lg hover:bg-accent-primary/90 transition-colors">
          Share Your First Agent
        </button>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map((agent) => (
        <AgentCard 
          key={agent.id} 
          agent={agent} 
          onLike={onLike}
          onDownload={onDownload}
        />
      ))}
    </div>
  )
}

function AgentCard({ agent, onLike, onDownload }) {
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

  return (
    <div className="bg-dark-surface rounded-xl border border-dark-border p-6 hover:border-accent-primary/50 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">{agent.name}</h3>
          <p className="text-sm text-gray-400">by {agent.author}</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onLike(agent.id)}
            className="p-2 hover:bg-dark-border rounded-lg transition-colors"
          >
            <Heart className={`w-4 h-4 ${agent.liked ? 'text-red-400 fill-current' : 'text-gray-400'}`} />
          </button>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-300 mb-4 line-clamp-3">{agent.description}</p>

      {/* Performance Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className={`text-lg font-bold ${getPerformanceColor(agent.totalReturn)}`}>
            {agent.totalReturn > 0 ? '+' : ''}{agent.totalReturn.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-400">Total Return</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-white">{agent.winRate}%</div>
          <div className="text-xs text-gray-400">Win Rate</div>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {agent.tags?.slice(0, 3).map((tag, index) => (
          <span key={index} className="px-2 py-1 bg-accent-primary/20 text-accent-primary text-xs rounded-md">
            {tag}
          </span>
        ))}
        {agent.tags?.length > 3 && (
          <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded-md">
            +{agent.tags.length - 3} more
          </span>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-dark-border">
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <div className="flex items-center space-x-1">
            <Eye className="w-4 h-4" />
            <span>{agent.views}</span>
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
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onDownload(agent.id)}
            className="px-3 py-1 bg-accent-primary text-white text-sm rounded-md hover:bg-accent-primary/90 transition-colors"
          >
            Download
          </button>
        </div>
      </div>

      <div className="text-xs text-gray-500 mt-2">
        Shared {formatDate(agent.sharedAt)}
      </div>
    </div>
  )
}

function ShareAgentForm({ userAgents, onShare, onCancel }) {
  const [selectedAgent, setSelectedAgent] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tags: '',
    strategy: '',
    isPublic: true
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const selectedAgentData = userAgents.find(agent => agent.id === selectedAgent)
    if (!selectedAgentData) return

    const shareData = {
      ...selectedAgentData,
      name: formData.name || selectedAgentData.name,
      description: formData.description,
      tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      isPublic: formData.isPublic,
      sharedAt: new Date().toISOString()
    }

    onShare(shareData)
  }

  const handleAgentSelect = (agentId) => {
    setSelectedAgent(agentId)
    const agent = userAgents.find(a => a.id === agentId)
    if (agent) {
      setFormData(prev => ({
        ...prev,
        name: agent.name || '',
        description: agent.description || '',
        strategy: agent.strategy || ''
      }))
    }
  }

  if (userAgents.length === 0) {
    return (
      <div className="bg-dark-surface rounded-xl border border-dark-border p-8 text-center">
        <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">No Agents to Share</h3>
        <p className="text-gray-400 mb-6">Create and backtest some trading agents first, then come back to share them with the community!</p>
        <button
          onClick={onCancel}
          className="bg-accent-primary text-white px-6 py-3 rounded-lg hover:bg-accent-primary/90 transition-colors"
        >
          Go Create Agents
        </button>
      </div>
    )
  }

  return (
    <div className="bg-dark-surface rounded-xl border border-dark-border p-8">
      <h2 className="text-2xl font-bold text-white mb-6">Share Your Agent</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Agent Selection */}
        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Select Agent to Share
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => handleAgentSelect(e.target.value)}
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:border-accent-primary focus:outline-none"
            required
          >
            <option value="">Choose an agent...</option>
            {userAgents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name || `Agent ${agent.id.slice(0, 8)}`} - {agent.totalReturn?.toFixed(1)}% return
              </option>
            ))}
          </select>
        </div>

        {/* Agent Name */}
        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Agent Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:border-accent-primary focus:outline-none"
            placeholder="Give your agent a memorable name..."
            required
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            rows={4}
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:border-accent-primary focus:outline-none resize-none"
            placeholder="Describe your strategy, what makes it unique, and any insights you've gained..."
            required
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={formData.tags}
            onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:border-accent-primary focus:outline-none"
            placeholder="momentum, RSI, swing trading, tech stocks..."
          />
        </div>

        {/* Privacy Setting */}
        <div>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.isPublic}
              onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
              className="w-4 h-4 text-accent-primary bg-dark-bg border-dark-border rounded focus:ring-accent-primary"
            />
            <span className="text-sm text-white">Make this agent public to the community</span>
          </label>
        </div>

        {/* Selected Agent Preview */}
        {selectedAgent && (
          <div className="bg-dark-bg rounded-lg p-4 border border-dark-border">
            <h4 className="text-sm font-medium text-white mb-2">Agent Preview</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Total Return:</span>
                <span className="text-white ml-2">
                  {userAgents.find(a => a.id === selectedAgent)?.totalReturn?.toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="text-gray-400">Win Rate:</span>
                <span className="text-white ml-2">
                  {userAgents.find(a => a.id === selectedAgent)?.winRate}%
                </span>
              </div>
              <div>
                <span className="text-gray-400">Total Trades:</span>
                <span className="text-white ml-2">
                  {userAgents.find(a => a.id === selectedAgent)?.totalTrades}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Symbol:</span>
                <span className="text-white ml-2">
                  {userAgents.find(a => a.id === selectedAgent)?.symbol}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end space-x-4 pt-6 border-t border-dark-border">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-3 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-6 py-3 bg-accent-primary text-white rounded-lg hover:bg-accent-primary/90 transition-colors flex items-center space-x-2"
          >
            <Share2 className="w-4 h-4" />
            <span>Share Agent</span>
          </button>
        </div>
      </form>
    </div>
  )
}
