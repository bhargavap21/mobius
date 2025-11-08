import { API_URL } from '../config'
import React, { useState } from 'react';

const StrategySidebar = ({
  isOpen,
  onClose,
  currentStrategy,
  onRefineStrategy,
  onRunBacktest
}) => {
  const [activeTab, setActiveTab] = useState('refine'); // 'refine', 'chat', 'insights'
  const [refinementRequest, setRefinementRequest] = useState('');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleRefine = async () => {
    if (!refinementRequest.trim()) return;

    console.log('[StrategySidebar] Starting refinement:', refinementRequest);

    // Build refinement prompt based on current strategy
    const refinementPrompt = `Modify this trading strategy: ${currentStrategy?.name || 'Current strategy'}

Current conditions:
- Asset: ${currentStrategy?.asset}
- Strategy type: ${currentStrategy?.strategy_type}
${currentStrategy?.rsi_period ? `- RSI period: ${currentStrategy.rsi_period}` : ''}
${currentStrategy?.rsi_oversold ? `- RSI oversold: ${currentStrategy.rsi_oversold}` : ''}
${currentStrategy?.rsi_overbought ? `- RSI overbought: ${currentStrategy.rsi_overbought}` : ''}

Requested changes: ${refinementRequest}`;

    // Call the refinement handler (which will close sidebar and show loading)
    onRefineStrategy(refinementPrompt);

    // Clear the input
    setRefinementRequest('');
  };

  const handleChat = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = chatMessage;
    setChatMessage('');

    // Add user message to chat
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          bot_context: {
            id: currentStrategy?.id,
            name: currentStrategy?.name,
            asset: currentStrategy?.asset,
            strategy_type: currentStrategy?.strategy_type,
            code: currentStrategy?.code,
            backtest_results: currentStrategy?.backtest_results,
            parameters: {
              rsi_period: currentStrategy?.rsi_period,
              rsi_oversold: currentStrategy?.rsi_oversold,
              rsi_overbought: currentStrategy?.rsi_overbought,
              sentiment_threshold: currentStrategy?.sentiment_threshold,
            }
          }
        }),
      });

      const data = await response.json();

      if (data.success) {
        setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        setChatHistory(prev => [...prev, {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        }]);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="w-full bg-[#0f1117] border-l border-white/10 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <h2 className="text-sm font-light text-white">Strategy Assistant</h2>
        <button
          onClick={onClose}
          className="text-white/50 hover:text-white text-2xl leading-none transition-colors"
        >
          ×
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10">
        <button
          onClick={() => setActiveTab('refine')}
          className={`flex-1 px-4 py-3 text-sm font-light ${
            activeTab === 'refine'
              ? 'text-accent border-b-2 border-accent bg-white/5'
              : 'text-white/50 hover:text-white hover:bg-white/5'
          }`}
        >
          Refine
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex-1 px-4 py-3 text-sm font-light ${
            activeTab === 'chat'
              ? 'text-accent border-b-2 border-accent bg-white/5'
              : 'text-white/50 hover:text-white hover:bg-white/5'
          }`}
        >
          Chat
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex-1 px-4 py-3 text-sm font-light ${
            activeTab === 'insights'
              ? 'text-accent border-b-2 border-accent bg-white/5'
              : 'text-white/50 hover:text-white hover:bg-white/5'
          }`}
        >
          Insights
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Refine Tab */}
        {activeTab === 'refine' && (
          <div className="space-y-5">
            <div>
              <h3 className="text-sm font-light text-white mb-3">Current Strategy</h3>
              <div className="bg-white/5 rounded-lg border border-white/10 p-4 text-sm text-white/80 space-y-2">
                <div><span className="text-white/50">Asset:</span> {currentStrategy?.asset}</div>
                <div><span className="text-white/50">Type:</span> {currentStrategy?.strategy_type}</div>
                {currentStrategy?.rsi_oversold && (
                  <div><span className="text-white/50">RSI Oversold:</span> {currentStrategy.rsi_oversold}</div>
                )}
                {currentStrategy?.rsi_overbought && (
                  <div><span className="text-white/50">RSI Overbought:</span> {currentStrategy.rsi_overbought}</div>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-light text-white mb-3">Suggest Improvements</h3>
              <p className="text-xs text-white/50 mb-3">
                Describe how you'd like to modify this strategy
              </p>

              {/* Quick suggestions */}
              <div className="space-y-2 mb-4">
                <button
                  onClick={() => setRefinementRequest('Make the entry conditions less restrictive - increase RSI threshold to 40')}
                  className="w-full text-left px-3 py-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-xs text-white/80 transition-colors"
                >
                  Loosen RSI threshold (30 → 40)
                </button>
                <button
                  onClick={() => setRefinementRequest('Lower the sentiment requirement to 0.1 instead of 0.2')}
                  className="w-full text-left px-3 py-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-xs text-white/80 transition-colors"
                >
                  Lower sentiment threshold
                </button>
                <button
                  onClick={() => setRefinementRequest('Change logic to use OR instead of AND for conditions')}
                  className="w-full text-left px-3 py-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-xs text-white/80 transition-colors"
                >
                  Use OR instead of AND
                </button>
                <button
                  onClick={() => setRefinementRequest('Remove sentiment requirement entirely, use only RSI')}
                  className="w-full text-left px-3 py-2 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-xs text-white/80 transition-colors"
                >
                  Remove sentiment filter
                </button>
              </div>

              <textarea
                value={refinementRequest}
                onChange={(e) => setRefinementRequest(e.target.value)}
                placeholder="E.g., 'Make RSI threshold 40 instead of 30' or 'Add a volume filter'"
                className="w-full h-32 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-accent resize-none"
              />
            </div>

            <button
              onClick={handleRefine}
              disabled={!refinementRequest.trim() || loading}
              className="w-full bg-accent hover:bg-accent/90 disabled:bg-accent/50 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              {loading ? 'Refining...' : 'Refine & Re-test'}
            </button>
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="flex flex-col h-full">
            <div className="flex-1 space-y-3 mb-4 overflow-y-auto">
              {chatHistory.length === 0 ? (
                <div className="text-center text-white/50 text-sm py-8">
                  <p className="mb-2">Ask me anything about:</p>
                  <ul className="text-xs space-y-1">
                    <li>• Why did my strategy execute 0 trades?</li>
                    <li>• What's a good RSI threshold?</li>
                    <li>• How can I improve my win rate?</li>
                    <li>• Explain sentiment scoring</li>
                  </ul>
                </div>
              ) : (
                chatHistory.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg text-sm ${
                      msg.role === 'user'
                        ? 'bg-accent text-white ml-8'
                        : 'bg-white/5 border border-white/10 text-white/80 mr-8'
                    }`}
                  >
                    {msg.content}
                  </div>
                ))
              )}
              {loading && (
                <div className="bg-white/5 border border-white/10 text-white/80 p-3 rounded-lg text-sm mr-8">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-accent border-t-transparent rounded-full"></div>
                    Thinking...
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                placeholder="Ask about your strategy..."
                className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-accent"
              />
              <button
                onClick={handleChat}
                disabled={!chatMessage.trim() || loading}
                className="px-4 py-2 bg-accent hover:bg-accent/90 disabled:bg-accent/50 disabled:opacity-50 text-white rounded-lg transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="space-y-4">
            <div className="bg-white/5 rounded-lg border border-white/10 p-4">
              <h3 className="text-sm font-light text-white mb-3">Strategy Analysis</h3>

              <div className="space-y-3 text-sm">
                {/* Performance Summary */}
                <div>
                  <div className="text-white/50 mb-1">Performance</div>
                  {currentStrategy?.backtest_results?.summary && (
                    <div className="text-white/80 space-y-1 text-xs">
                      <div>Trades: {currentStrategy.backtest_results.summary.total_trades || 0}</div>
                      <div>Win Rate: {currentStrategy.backtest_results.summary.win_rate?.toFixed(1) || 0}%</div>
                      <div>Total Return: {currentStrategy.backtest_results.summary.total_return?.toFixed(2) || 0}%</div>
                      <div>Sharpe Ratio: {currentStrategy.backtest_results.summary.sharpe_ratio?.toFixed(2) || 'N/A'}</div>
                    </div>
                  )}
                </div>

                {/* Overall Analysis */}
                {currentStrategy?.final_analysis?.analysis && (
                  <div>
                    <div className="text-white/50 mb-1">Analysis</div>
                    <div className="text-white/80 text-xs">
                      {currentStrategy.final_analysis.analysis}
                    </div>
                  </div>
                )}

                {/* Issues Detected */}
                {currentStrategy?.final_analysis?.issues && currentStrategy.final_analysis.issues.length > 0 && (
                  <div>
                    <div className="text-white/50 mb-1">Issues Detected</div>
                    <ul className="text-yellow-400 space-y-1 text-xs">
                      {currentStrategy.final_analysis.issues.map((issue, idx) => (
                        <li key={idx}>• {issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {currentStrategy?.final_analysis?.suggestions && currentStrategy.final_analysis.suggestions.length > 0 && (
                  <div>
                    <div className="text-white/50 mb-1">Recommendations</div>
                    <ul className="text-white/80 space-y-1 text-xs">
                      {currentStrategy.final_analysis.suggestions.map((suggestion, idx) => (
                        <li key={idx}>• {suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Fallback if no analysis data */}
                {!currentStrategy?.final_analysis && (
                  <div className="text-white/50 text-xs text-center py-4">
                    No analysis data available yet
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => setActiveTab('refine')}
              className="w-full bg-accent hover:bg-accent/90 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Go to Refine Tab →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategySidebar;
