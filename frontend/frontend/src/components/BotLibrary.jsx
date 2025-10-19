import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import BotsGrid from './bots/BotsGrid';

const BotLibrary = ({ onClose, onLoadBot, user, onSignOut, onShowBotLibrary }) => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    loadBots();
  }, []);

  const loadBots = async () => {
    setLoading(true);
    setError('');

    try {
      // Always fetch all bots - filtering will be done client-side
      const url = 'http://localhost:8000/bots?page=1&page_size=50';

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
      const botList = data.data || [];
      setBots(botList);
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
          id: bot.id,
          name: bot.name,
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
    <div className="fixed inset-0 bg-dark-bg flex flex-col z-50">
      {/* Navbar at the very top */}
      <div className="flex items-center justify-between p-6 border-b border-dark-border bg-dark-surface/50 backdrop-blur-sm">
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

      {/* Main Content - Borderless page with grid */}
      <div className="flex-1 overflow-y-auto">
        <main className="mx-auto w-full max-w-6xl px-6 py-10">
          <h1 className="mb-8 text-4xl md:text-5xl font-light text-white leading-tight">My Trading Bots</h1>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400">
              <p className="font-medium">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-20 text-gray-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-accent mb-4"></div>
              <p>Loading bots...</p>
            </div>
          ) : (
            <BotsGrid
              bots={bots}
              onToggleFavorite={toggleFavorite}
              onDelete={deleteBot}
              onLoad={loadBotDetails}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default BotLibrary;
