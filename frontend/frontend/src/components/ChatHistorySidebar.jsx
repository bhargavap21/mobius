import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Plus, MessageSquare, Trash2, Star, Calendar } from 'lucide-react';

const ChatHistorySidebar = ({ onClose, onLoadBot, onNewChat, currentBotId }) => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { getAuthHeaders, user } = useAuth();

  useEffect(() => {
    loadBots();
  }, []);

  const loadBots = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/bots?page=1&page_size=100', {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Failed to load chat history');
      }

      const data = await response.json();
      setBots(data.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteBot = async (botId, e) => {
    e.stopPropagation(); // Prevent loading the bot when clicking delete

    if (!confirm('Are you sure you want to delete this bot?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/bots/${botId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Failed to delete bot');
      }

      setBots(bots.filter(bot => bot.id !== botId));
    } catch (err) {
      console.error('Error deleting bot:', err);
      alert('Failed to delete bot');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  // Group bots by date
  const groupedBots = bots.reduce((groups, bot) => {
    const date = formatDate(bot.created_at);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(bot);
    return groups;
  }, {});

  return (
    <div className="h-screen w-64 bg-[#0a0a0a] border-r border-gray-800 flex flex-col sticky top-0">
      {/* Header with top padding to align with main content */}
      <div className="p-4 border-b border-gray-800 mt-2">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-700 rounded-lg hover:bg-gray-800 transition-all duration-200 text-gray-200 font-medium text-sm"
        >
          <Plus className="w-4 h-4" />
          New Strategy
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-2">
        {loading && (
          <div className="flex items-center justify-center p-8 text-gray-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          </div>
        )}

        {error && (
          <div className="p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        {!loading && !error && Object.keys(groupedBots).length === 0 && (
          <div className="p-4 text-gray-500 text-sm text-center">
            No chat history yet
          </div>
        )}

        {!loading && !error && Object.keys(groupedBots).map(date => (
          <div key={date} className="mb-4">
            {/* Date Header */}
            <div className="px-2 py-1 text-xs text-gray-500 font-medium">
              {date}
            </div>

            {/* Bots for this date */}
            {groupedBots[date].map(bot => (
              <button
                key={bot.id}
                onClick={() => onLoadBot(bot)}
                className={`w-full group flex items-start gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-all duration-150 text-left mb-1 ${
                  currentBotId === bot.id ? 'bg-gray-800' : ''
                }`}
              >
                <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />

                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-200 truncate">
                    {bot.name || 'Unnamed Strategy'}
                  </div>
                  {bot.strategy_config?.asset && (
                    <div className="text-xs text-gray-500 truncate">
                      {bot.strategy_config.asset}
                    </div>
                  )}
                </div>

                {/* Delete button */}
                <button
                  onClick={(e) => deleteBot(bot.id, e)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded"
                  title="Delete"
                >
                  <Trash2 className="w-3.5 h-3.5 text-red-400" />
                </button>

                {/* Favorite indicator */}
                {bot.is_favorite && (
                  <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400 flex-shrink-0" />
                )}
              </button>
            ))}
          </div>
        ))}
      </div>

      {/* Footer */}
      {user && (
        <div className="p-4 border-t border-gray-800">
          <div className="text-sm text-gray-400 truncate">
            {user.email}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistorySidebar;
