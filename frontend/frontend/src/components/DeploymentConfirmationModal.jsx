import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, DollarSign, Clock, TrendingUp, Shield } from 'lucide-react';

const DeploymentConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  deploymentConfig,
  strategy,
  backtestResults,
  isPaperTrading
}) => {
  const [hasReadWarnings, setHasReadWarnings] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [acknowledgedRisks, setAcknowledgedRisks] = useState({
    lossOfCapital: false,
    noGuarantees: false,
    ownRisk: false,
    paperVsLive: false
  });

  if (!isOpen) return null;

  const allRisksAcknowledged = Object.values(acknowledgedRisks).every(v => v);
  const confirmationPhrase = isPaperTrading ? "START PAPER TRADING" : "START LIVE TRADING";
  const isConfirmationValid = confirmText === confirmationPhrase && allRisksAcknowledged && hasReadWarnings;

  const handleConfirm = () => {
    if (isConfirmationValid) {
      onConfirm();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-dark-surface border border-dark-border rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`px-6 py-4 border-b ${isPaperTrading ? 'border-blue-500/30 bg-blue-500/10' : 'border-red-500/30 bg-red-500/10'}`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              {isPaperTrading ? (
                <Shield className="w-6 h-6 text-blue-400" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-red-400" />
              )}
              <div>
                <h2 className="text-xl font-semibold text-white">
                  {isPaperTrading ? 'Deploy to Paper Trading' : 'Deploy to Live Trading'}
                </h2>
                <p className="text-sm text-gray-400 mt-1">
                  {isPaperTrading
                    ? 'Test your strategy with simulated trading'
                    : 'REAL MONEY - Please review carefully'}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <XCircle className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Deployment Summary */}
        <div className="px-6 py-4 border-b border-dark-border">
          <h3 className="text-sm font-semibold text-white mb-3">Deployment Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-dark-bg rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                <DollarSign className="w-4 h-4" />
                Initial Capital
              </div>
              <div className="text-white text-lg font-semibold">
                ${deploymentConfig.initialCapital.toLocaleString()}
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                <Clock className="w-4 h-4" />
                Execution Frequency
              </div>
              <div className="text-white text-lg font-semibold">
                {deploymentConfig.executionFrequency}
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                <TrendingUp className="w-4 h-4" />
                Max Position Size
              </div>
              <div className="text-white text-lg font-semibold">
                ${deploymentConfig.maxPositionSize?.toLocaleString() || 'No Limit'}
              </div>
            </div>
            <div className="bg-dark-bg rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                <Shield className="w-4 h-4" />
                Daily Loss Limit
              </div>
              <div className="text-white text-lg font-semibold">
                ${deploymentConfig.dailyLossLimit?.toLocaleString() || 'No Limit'}
              </div>
            </div>
          </div>
        </div>

        {/* Strategy Info */}
        <div className="px-6 py-4 border-b border-dark-border">
          <h3 className="text-sm font-semibold text-white mb-3">Strategy Details</h3>
          <div className="bg-dark-bg rounded-lg p-3 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Asset:</span>
              <span className="text-white font-medium">{strategy?.asset || 'N/A'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Strategy Type:</span>
              <span className="text-white font-medium">{strategy?.strategy_type || 'N/A'}</span>
            </div>
            {backtestResults && (
              <>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Backtest Return:</span>
                  <span className={`font-medium ${backtestResults.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {backtestResults.total_return?.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Win Rate:</span>
                  <span className="text-white font-medium">{backtestResults.win_rate?.toFixed(1)}%</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Risk Warnings */}
        <div className="px-6 py-4 border-b border-dark-border">
          <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Risk Disclosure
          </h3>
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 space-y-3">
            <div className="flex items-start gap-2">
              <input
                type="checkbox"
                id="risk-loss"
                checked={acknowledgedRisks.lossOfCapital}
                onChange={(e) => setAcknowledgedRisks({...acknowledgedRisks, lossOfCapital: e.target.checked})}
                className="mt-1"
              />
              <label htmlFor="risk-loss" className="text-sm text-gray-300">
                I understand that trading involves substantial risk of loss and I can lose all or more than my initial investment.
              </label>
            </div>
            <div className="flex items-start gap-2">
              <input
                type="checkbox"
                id="risk-guarantees"
                checked={acknowledgedRisks.noGuarantees}
                onChange={(e) => setAcknowledgedRisks({...acknowledgedRisks, noGuarantees: e.target.checked})}
                className="mt-1"
              />
              <label htmlFor="risk-guarantees" className="text-sm text-gray-300">
                I understand that past backtest performance is not indicative of future results and there are no guarantees of profit.
              </label>
            </div>
            <div className="flex items-start gap-2">
              <input
                type="checkbox"
                id="risk-own"
                checked={acknowledgedRisks.ownRisk}
                onChange={(e) => setAcknowledgedRisks({...acknowledgedRisks, ownRisk: e.target.checked})}
                className="mt-1"
              />
              <label htmlFor="risk-own" className="text-sm text-gray-300">
                I understand that I am solely responsible for all trading decisions and any losses incurred.
              </label>
            </div>
            {!isPaperTrading && (
              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="risk-live"
                  checked={acknowledgedRisks.paperVsLive}
                  onChange={(e) => setAcknowledgedRisks({...acknowledgedRisks, paperVsLive: e.target.checked})}
                  className="mt-1"
                />
                <label htmlFor="risk-live" className="text-sm text-gray-300">
                  I understand this will execute REAL trades with REAL MONEY and I should test thoroughly in paper trading first.
                </label>
              </div>
            )}
          </div>
        </div>

        {/* Safety Features */}
        <div className="px-6 py-4 border-b border-dark-border">
          <h3 className="text-sm font-semibold text-white mb-3">Active Safety Features</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Daily loss limit: ${deploymentConfig.dailyLossLimit || 'Not set'}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Maximum position size: ${deploymentConfig.maxPositionSize || 'Not set'}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Market hours only: Enabled</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Emergency stop available at any time</span>
            </div>
          </div>
        </div>

        {/* Confirmation Input */}
        <div className="px-6 py-4">
          <div className="mb-4">
            <label className="flex items-start gap-2 text-sm text-gray-300 mb-3">
              <input
                type="checkbox"
                checked={hasReadWarnings}
                onChange={(e) => setHasReadWarnings(e.target.checked)}
                className="mt-1"
              />
              <span>I have read and understand all warnings above</span>
            </label>
          </div>

          {hasReadWarnings && allRisksAcknowledged && (
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Type "{confirmationPhrase}" to confirm deployment:
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-accent"
                placeholder={confirmationPhrase}
                autoFocus
              />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-dark-border flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-dark-border rounded-lg text-gray-300 hover:bg-dark-bg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!isConfirmationValid}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              isConfirmationValid
                ? isPaperTrading
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isPaperTrading ? 'Start Paper Trading' : 'Start Live Trading'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeploymentConfirmationModal;
