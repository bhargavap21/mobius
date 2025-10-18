import React, { useMemo, useState } from 'react';
import BotCard from './BotCard';
import EmptyBots from './EmptyBots';

const BotsGrid = ({ bots, onToggleFavorite, onDelete, onLoad }) => {
  const [tab, setTab] = useState('all');

  const items = useMemo(() => {
    // Map raw bot data to BotCard props
    const mapped = bots.map((b) => ({
      id: b.id,
      name: b.name || 'Untitled Bot',
      url: b.description || b.symbol || b.share_url || '—',
      updatedAt: b.created_at 
        ? new Date(b.created_at).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
          })
        : '',
      branch: b.branch || 'main',
      isFavorite: Boolean(b.is_favorite),
      status: b.status || 'ok',
      totalTrades: b.total_trades ?? null,
      totalReturn: b.total_return ?? null,
      winRate: b.win_rate ?? null,
      // Store raw bot for callbacks
      _raw: b,
    }));

    return tab === 'favorites' ? mapped.filter((m) => m.isFavorite) : mapped;
  }, [bots, tab]);

  if (!bots || bots.length === 0) {
    return <EmptyBots />;
  }

  if (items.length === 0 && tab === 'favorites') {
    return (
      <div>
        <div className="mb-6 flex items-center gap-4 border-b border-white/10 pb-2">
          <button
            className={`text-sm transition-colors pb-2 ${tab === 'all' ? 'text-white border-b-2 border-accent' : 'text-white/50 hover:text-white'}`}
            onClick={() => setTab('all')}
            type="button"
          >
            All Bots
          </button>
          <button
            className={`text-sm transition-colors pb-2 flex items-center gap-1 ${tab === 'favorites' ? 'text-white border-b-2 border-accent' : 'text-white/50 hover:text-white'}`}
            onClick={() => setTab('favorites')}
            type="button"
          >
            ★ Favorites
          </button>
        </div>
        <div className="rounded-2xl border border-white/10 bg-transparent p-8 text-center text-white/50">
          No favorite bots yet. Click the star icon on a bot to add it to favorites.
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6 flex items-center gap-4 border-b border-white/10 pb-2">
        <button
          className={`text-sm transition-colors pb-2 ${tab === 'all' ? 'text-white border-b-2 border-accent' : 'text-white/50 hover:text-white'}`}
          onClick={() => setTab('all')}
          type="button"
        >
          All Bots
        </button>
        <button
          className={`text-sm transition-colors pb-2 flex items-center gap-1 ${tab === 'favorites' ? 'text-white border-b-2 border-accent' : 'text-white/50 hover:text-white'}`}
          onClick={() => setTab('favorites')}
          type="button"
        >
          ★ Favorites
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {items.map((bot) => (
          <BotCard
            key={bot.id}
            bot={bot}
            onToggleFavorite={onToggleFavorite}
            onDelete={onDelete}
            onLoad={onLoad}
          />
        ))}
      </div>
    </>
  );
};

export default BotsGrid;

