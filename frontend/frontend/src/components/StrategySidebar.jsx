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

    setLoading(true);
    try {
      // Build refinement prompt based on current strategy
      const refinementPrompt = `Modify this trading strategy: ${currentStrategy?.name || 'Current strategy'}

Current conditions:
- Asset: ${currentStrategy?.asset}
- Strategy type: ${currentStrategy?.strategy_type}
${currentStrategy?.rsi_period ? `- RSI period: ${currentStrategy.rsi_period}` : ''}
${currentStrategy?.rsi_oversold ? `- RSI oversold: ${currentStrategy.rsi_oversold}` : ''}
${currentStrategy?.rsi_overbought ? `- RSI overbought: ${currentStrategy.rsi_overbought}` : ''}

Requested changes: ${refinementRequest}`;

      onRefineStrategy(refinementPrompt);
      setRefinementRequest('');
      onClose();
    } catch (error) {
      console.error('Error refining strategy:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = chatMessage;
    setChatMessage('');

    // Add user message to chat
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
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
    <div className="w-96 bg-gray-800 border-l border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
        <h2 className="text-lg font-bold text-white">Strategy Assistant</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-2xl leading-none"
        >
          ×
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        <button
          onClick={() => setActiveTab('refine')}
          className={`flex-1 px-4 py-3 text-sm font-medium ${
            activeTab === 'refine'
              ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-750'
              : 'text-gray-400 hover:text-white hover:bg-gray-750'
          }`}
        >
          🔧 Refine
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex-1 px-4 py-3 text-sm font-medium ${
            activeTab === 'chat'
              ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-750'
              : 'text-gray-400 hover:text-white hover:bg-gray-750'
          }`}
        >
          💬 Chat
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex-1 px-4 py-3 text-sm font-medium ${
            activeTab === 'insights'
              ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-750'
              : 'text-gray-400 hover:text-white hover:bg-gray-750'
          }`}
        >
          💡 Insights
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Refine Tab */}
        {activeTab === 'refine' && (
          <div className="space-y-5">
            <div>
              <h3 className="text-sm font-semibold text-white mb-3">Current Strategy</h3>
              <div className="bg-gray-900 rounded p-4 text-sm text-gray-300 space-y-2">
                <div><span className="text-gray-500">Asset:</span> {currentStrategy?.asset}</div>
                <div><span className="text-gray-500">Type:</span> {currentStrategy?.strategy_type}</div>
                {currentStrategy?.rsi_oversold && (
                  <div><span className="text-gray-500">RSI Oversold:</span> {currentStrategy.rsi_oversold}</div>
                )}
                {currentStrategy?.rsi_overbought && (
                  <div><span className="text-gray-500">RSI Overbought:</span> {currentStrategy.rsi_overbought}</div>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-white mb-3">Suggest Improvements</h3>
              <p className="text-xs text-gray-400 mb-3">
                Describe how you'd like to modify this strategy
              </p>

              {/* Quick suggestions */}
              <div className="space-y-2 mb-4">
                <button
                  onClick={() => setRefinementRequest('Make the entry conditions less restrictive - increase RSI threshold to 40')}
                  className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-650 rounded text-xs text-gray-300"
                >
                  💡 Loosen RSI threshold (30 → 40)
                </button>
                <button
                  onClick={() => setRefinementRequest('Lower the sentiment requirement to 0.1 instead of 0.2')}
                  className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-650 rounded text-xs text-gray-300"
                >
                  💡 Lower sentiment threshold
                </button>
                <button
                  onClick={() => setRefinementRequest('Change logic to use OR instead of AND for conditions')}
                  className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-650 rounded text-xs text-gray-300"
                >
                  💡 Use OR instead of AND
                </button>
                <button
                  onClick={() => setRefinementRequest('Remove sentiment requirement entirely, use only RSI')}
                  className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-650 rounded text-xs text-gray-300"
                >
                  💡 Remove sentiment filter
                </button>
              </div>

              <textarea
                value={refinementRequest}
                onChange={(e) => setRefinementRequest(e.target.value)}
                placeholder="E.g., 'Make RSI threshold 40 instead of 30' or 'Add a volume filter'"
                className="w-full h-32 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500 resize-none"
              />
            </div>

            <button
              onClick={handleRefine}
              disabled={!refinementRequest.trim() || loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded transition-colors"
            >
              {loading ? 'Refining...' : '🚀 Refine & Re-test'}
            </button>
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="flex flex-col h-full">
            <div className="flex-1 space-y-3 mb-4 overflow-y-auto">
              {chatHistory.length === 0 ? (
                <div className="text-center text-gray-400 text-sm py-8">
                  <p className="mb-2">💬 Ask me anything about:</p>
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
                    className={`p-3 rounded text-sm ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white ml-8'
                        : 'bg-gray-700 text-gray-200 mr-8'
                    }`}
                  >
                    {msg.content}
                  </div>
                ))
              )}
              {loading && (
                <div className="bg-gray-700 text-gray-200 p-3 rounded text-sm mr-8">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
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
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={handleChat}
                disabled={!chatMessage.trim() || loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="space-y-4">
            <div className="bg-gray-900 rounded p-4">
              <h3 className="text-sm font-semibold text-white mb-3">📊 Strategy Analysis</h3>

              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Performance</div>
                  <div className="text-yellow-400">
                    ⚠️ 0 trades executed - conditions too restrictive
                  </div>
                </div>

                <div>
                  <div className="text-gray-400 mb-1">Issue Detected</div>
                  <div className="text-gray-300">
                    RSI &lt; 30 (oversold) rarely occurs when sentiment is bullish.
                    These conditions conflict.
                  </div>
                </div>

                <div>
                  <div className="text-gray-400 mb-1">Recommendations</div>
                  <ul className="text-gray-300 space-y-1 text-xs">
                    <li>• Increase RSI threshold to 40-50</li>
                    <li>• Lower sentiment requirement to 0.1</li>
                    <li>• Use OR logic instead of AND</li>
                    <li>• Remove one of the filters</li>
                  </ul>
                </div>
              </div>
            </div>

            <button
              onClick={() => setActiveTab('refine')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition-colors"
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
