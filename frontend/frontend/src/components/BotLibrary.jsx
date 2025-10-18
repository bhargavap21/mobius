import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const BotLibrary = ({ onClose, onLoadBot, user, onSignOut, onShowBotLibrary }) => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // 'all' or 'favorites'

  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    loadBots();
  }, [filter]);

  const loadBots = async () => {
    setLoading(true);
    setError('');

    try {
      const url = filter === 'favorites'
        ? 'http://localhost:8000/bots/favorites'
        : 'http://localhost:8000/bots?page=1&page_size=50';

      const headers = getAuthHeaders();
      console.log('[BotLibrary] Auth headers:', headers);

      const response = await fetch(url, {
        headers: {
          ...headers,
        },
      });

      console.log('[BotLibrary] Response status:', response.status);

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please try signing out and back in.');
        }
        throw new Error('Failed to load bots');
      }

      const data = await response.json();

      // Handle both paginated response and favorites array
      const botList = filter === 'favorites' ? data : data.data;
      setBots(botList || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (botId, currentStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/bots/${botId}/favorite`, {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error('Failed to toggle favorite');
      }

      // Update local state
      setBots(bots.map(bot =>
        bot.id === botId ? { ...bot, is_favorite: !currentStatus } : bot
      ));
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const deleteBot = async (botId) => {
    if (!confirm('Are you sure you want to delete this bot?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/bots/${botId}`, {
        method: 'DELETE',
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete bot');
      }

      setBots(bots.filter(bot => bot.id !== botId));
    } catch (err) {
      console.error('Error deleting bot:', err);
    }
  };

  const loadBotDetails = async (botId) => {
    try {
      const response = await fetch(`http://localhost:8000/bots/${botId}`, {
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load bot details');
      }

      const bot = await response.json();

      // Pass bot data to parent component
      if (onLoadBot) {
        onLoadBot({
          strategy: bot.strategy_config,
          code: bot.generated_code,
          backtest_results: bot.backtest_results,
          insights_config: bot.insights_config,
        });
        onClose();
      }
    } catch (err) {
      console.error('Error loading bot details:', err);
      setError('Failed to load bot details');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex flex-col z-50">
      {/* Navbar at the very top */}
      <div className="flex items-center justify-between p-6 border-b border-gray-700 bg-dark-surface/50 backdrop-blur-sm">
        <button
          onClick={onClose}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-sm">Back to AI</span>
        </button>

        <div className="flex items-center gap-3">
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
              
              {/* Dropdown Menu */}
              <div className="absolute right-0 top-full mt-1 w-32 bg-dark-surface border border-dark-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="py-1">
                  <button
                    onClick={onShowBotLibrary}
                    className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-dark-bg hover:text-white transition-colors"
                  >
                    📚 My Bots
                  </button>
                  <button
                    onClick={onSignOut}
                    className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-dark-bg hover:text-red-300 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>
      </div>

      {/* Modal content */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="bg-gray-800 rounded-lg p-8 max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">My Trading Bots</h2>
          </div>

        {/* Filter tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-700">
          <button
            onClick={() => setFilter('all')}
            className={`pb-2 px-1 ${
              filter === 'all'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            All Bots
          </button>
          <button
            onClick={() => setFilter('favorites')}
            className={`pb-2 px-1 ${
              filter === 'favorites'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            ⭐ Favorites
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900 bg-opacity-50 border border-red-500 rounded text-red-200 text-sm">
            {error}
          </div>
        )}

        {/* Bot list */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="text-center py-12 text-gray-400">
              Loading bots...
            </div>
          ) : bots.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              {filter === 'favorites'
                ? 'No favorite bots yet. Star some bots to see them here!'
                : 'No bots saved yet. Create your first trading bot to get started!'
              }
            </div>
          ) : (
            <div className="space-y-4">
              {bots.map((bot) => (
                <div
                  key={bot.id}
                  className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-white">
                          {bot.name}
                        </h3>
                        <button
                          onClick={() => toggleFavorite(bot.id, bot.is_favorite)}
                          className="text-xl hover:scale-110 transition-transform"
                        >
                          {bot.is_favorite ? '⭐' : '☆'}
                        </button>
                      </div>
                      {bot.description && (
                        <p className="text-gray-400 text-sm mt-1">
                          {bot.description}
                        </p>
                      )}
                    </div>
                    <div className="text-right text-sm text-gray-400">
                      {new Date(bot.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Performance metrics */}
                  {(bot.total_trades !== null || bot.total_return !== null) && (
                    <div className="flex gap-4 mb-3 text-sm">
                      {bot.total_trades !== null && (
                        <div className="text-gray-300">
                          <span className="text-gray-400">Trades:</span>{' '}
                          <span className="font-semibold">{bot.total_trades}</span>
                        </div>
                      )}
                      {bot.total_return !== null && (
                        <div className="text-gray-300">
                          <span className="text-gray-400">Return:</span>{' '}
                          <span
                            className={`font-semibold ${
                              bot.total_return > 0 ? 'text-green-400' : 'text-red-400'
                            }`}
                          >
                            {bot.total_return > 0 ? '+' : ''}
                            {bot.total_return.toFixed(1)}%
                          </span>
                        </div>
                      )}
                      {bot.win_rate !== null && (
                        <div className="text-gray-300">
                          <span className="text-gray-400">Win Rate:</span>{' '}
                          <span className="font-semibold">
                            {(bot.win_rate * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => loadBotDetails(bot.id)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                    >
                      Load Bot
                    </button>
                    <button
                      onClick={() => deleteBot(bot.id)}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        </div>
      </div>
    </div>
  );
};

export default BotLibrary;
