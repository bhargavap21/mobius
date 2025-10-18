import React from 'react';
import { Activity, Star, MoreHorizontal } from 'lucide-react';

const BotCard = ({ bot, onToggleFavorite, onDelete, onLoad }) => {
  const handleFavoriteClick = (e) => {
    e.preventDefault();
    if (onToggleFavorite) {
      onToggleFavorite(bot.id, bot.isFavorite);
    }
  };

  const handleMoreClick = (e) => {
    e.preventDefault();
    if (onDelete) {
      onDelete(bot.id);
    }
  };

  const handleCardClick = (e) => {
    // Only trigger load if clicking on the card itself, not buttons
    if (e.target === e.currentTarget || e.target.closest('.bot-card-content')) {
      if (onLoad) {
        onLoad(bot.id);
      }
    }
  };

  return (
    <div
      onClick={handleCardClick}
      className="group relative block rounded-2xl border border-white/10 bg-[#0e1117] p-5 transition cursor-pointer hover:border-accent/50 hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleCardClick(e);
        }
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 bot-card-content flex-1">
          <div className="grid h-10 w-10 place-items-center rounded-full bg-white/5 text-white/70 flex-shrink-0">
            <Activity className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold tracking-tight text-white group-hover:text-white truncate">
              {bot.name}
            </h3>
            <p className="mt-0.5 line-clamp-1 text-sm text-white/50">
              {bot.url ?? "—"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            aria-label="Delete bot"
            className="rounded-full p-1.5 text-white/50 hover:bg-white/10 hover:text-white/80 transition-colors"
            onClick={handleMoreClick}
            type="button"
          >
            <MoreHorizontal className="h-4 w-4" />
          </button>
          <button
            aria-label={bot.isFavorite ? "Unfavorite" : "Favorite"}
            className={`rounded-full p-1.5 ${bot.isFavorite ? "text-accent" : "text-white/40"} hover:bg-white/10 transition-colors`}
            onClick={handleFavoriteClick}
            type="button"
          >
            <Star className={`h-4 w-4 ${bot.isFavorite ? "fill-current" : ""}`} />
          </button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-white/50">
        {bot.branch && (
          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5">
            {bot.branch}
          </span>
        )}
        {bot.status && (
          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5">
            {bot.status}
          </span>
        )}
        {bot.updatedAt && (
          <span className="ml-auto">Last run: {bot.updatedAt}</span>
        )}
      </div>

      {/* Performance metrics */}
      {(bot.totalTrades !== null || bot.totalReturn !== null || bot.winRate !== null) && (
        <div className="mt-3 pt-3 border-t border-white/10 flex flex-wrap gap-3 text-xs">
          {bot.totalTrades !== null && (
            <div className="text-gray-300">
              <span className="text-white/50">Trades:</span>{' '}
              <span className="font-semibold text-white">{bot.totalTrades}</span>
            </div>
          )}
          {bot.totalReturn !== null && (
            <div className="text-gray-300">
              <span className="text-white/50">Return:</span>{' '}
              <span
                className={`font-semibold ${
                  bot.totalReturn > 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {bot.totalReturn > 0 ? '+' : ''}
                {bot.totalReturn.toFixed(1)}%
              </span>
            </div>
          )}
          {bot.winRate !== null && (
            <div className="text-gray-300">
              <span className="text-white/50">Win Rate:</span>{' '}
              <span className="font-semibold text-white">
                {(bot.winRate * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BotCard;

