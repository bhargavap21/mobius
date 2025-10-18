import React from 'react';

const EmptyBots = () => {
  return (
    <div className="rounded-2xl border border-white/10 bg-transparent p-12 text-center">
      <div className="mx-auto max-w-md">
        <div className="mb-4 text-4xl">🤖</div>
        <h3 className="text-lg font-semibold text-white mb-2">No bots yet</h3>
        <p className="text-white/50 text-sm">
          Click <span className="text-accent font-medium">Build Bot</span> to create your first trading bot.
        </p>
      </div>
    </div>
  );
};

export default EmptyBots;

