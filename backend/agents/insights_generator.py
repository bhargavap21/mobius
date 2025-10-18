"""
Insights Generator Agent
Analyzes user query and backtest results to generate helpful visualizations and insights
"""
import logging
from typing import Dict, Any, List
from llm_client import generate_json, generate_text

logger = logging.getLogger(__name__)


class InsightsGeneratorAgent:
    """Generates additional insights and visualizations based on strategy context"""

    def __init__(self):
        pass

    async def analyze_query_for_insights(self, user_query: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user query to determine what additional visualizations would be helpful

        Returns:
        {
            "visualizations": [
                {
                    "type": "indicator" | "sentiment" | "price_action" | "custom",
                    "title": "Chart Title",
                    "description": "What this chart shows",
                    "data_keys": ["key1", "key2"],  # What data to collect
                    "threshold_keys": ["threshold1"],  # User-specified thresholds to show
                    "y_axis_config": {"domain": [0, 100], "label": "RSI"},
                    "reference_lines": [{"value": 30, "label": "Buy Threshold", "color": "green"}]
                }
            ],
            "insights": [
                "Key insight 1",
                "Key insight 2"
            ]
        }
        """

        prompt = f"""Analyze this trading strategy query and determine what visualizations would help the user understand their backtest results:

User Query: {user_query}

Strategy Details:
{strategy}

Your task:
1. Identify the KEY CONDITIONS that drive this strategy (entry/exit triggers)
2. Determine what data visualizations would help verify the strategy is working correctly
3. For each visualization, specify exactly what data needs to be collected

Common visualization types:
- **Technical Indicators**: RSI, MACD, SMA, Bollinger Bands, etc.
- **Sentiment Analysis**: Twitter/Reddit sentiment scores over time
- **Price Action**: Support/resistance levels, breakouts, volume
- **News/Events**: Impact of news events on price
- **Volatility**: ATR, price volatility over time
- **Custom Metrics**: Any other relevant data

Return a JSON object with this structure:
{{
    "visualizations": [
        {{
            "type": "indicator|sentiment|price_action|custom",
            "title": "Clear, descriptive title",
            "description": "1-2 sentence explanation of what this shows and why it's useful",
            "data_to_collect": {{
                "primary_metric": "The main data point to track (e.g., 'rsi', 'reddit_sentiment')",
                "additional_metrics": ["Any supporting metrics"],
                "thresholds": {{"key": "threshold_name", "description": "What this threshold means"}}
            }},
            "chart_config": {{
                "y_axis": {{"min": 0, "max": 100, "label": "Y-axis label"}},
                "zones": [{{"start": 0, "end": 30, "label": "Oversold", "color": "red"}}],
                "reference_lines": [{{"key": "threshold", "label": "Entry Threshold", "color": "green"}}]
            }}
        }}
    ],
    "insights": [
        "Key insight about what to look for in the data",
        "Common pitfall or thing to verify"
    ]
}}

IMPORTANT: Only suggest visualizations that are DIRECTLY RELEVANT to understanding this specific strategy. Don't add generic charts.

Examples:

Query: "Buy GME when Reddit sentiment > 0.5"
→ Chart: Reddit sentiment over time with 0.5 threshold line
→ Insight: "Sentiment rarely exceeds 0.5; most bullish scores are 0.2-0.4"

Query: "Buy AAPL when RSI < 30, sell when RSI > 70"
→ Chart: RSI over time with both 30 and 70 threshold lines
→ Insight: "RSI < 30 is rare for AAPL, occurring only a few times per year"

Query: "Buy TSLA after Elon tweets"
→ Chart: Tweet frequency and sentiment correlation with price
→ Insight: "Verify tweets are being detected on correct dates"

Now analyze the user's query:"""

        try:
            logger.info(f"Calling Gemini to generate insights config...")
            insights_config = generate_json(prompt, max_tokens=2000)
            logger.info(f"✅ Generated {len(insights_config.get('visualizations', []))} visualization configs")
            return insights_config

        except Exception as e:
            logger.error(f"❌ Error generating insights config: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "visualizations": [],
                "insights": []
            }

    async def generate_chart_interpretation(
        self,
        user_query: str,
        visualization_config: Dict[str, Any],
        chart_data: List[Dict[str, Any]],
        backtest_summary: Dict[str, Any]
    ) -> str:
        """
        Generate natural language interpretation of a chart
        """

        # Sample data points for analysis
        sample_size = min(10, len(chart_data))
        sample_data = chart_data[::len(chart_data)//sample_size] if len(chart_data) > sample_size else chart_data

        prompt = f"""Analyze this chart data and provide a concise interpretation for the user.

User's Strategy: {user_query}

Chart: {visualization_config['title']}
Description: {visualization_config['description']}

Sample Data Points (showing {sample_size} of {len(chart_data)} points):
{sample_data}

Backtest Results:
- Total Trades: {backtest_summary.get('total_trades', 0)}
- Win Rate: {backtest_summary.get('win_rate', 0)}%
- Total Return: {backtest_summary.get('total_return', 0)}%

Provide a 2-3 sentence interpretation that:
1. Describes what the data shows
2. Explains why the strategy performed the way it did
3. Suggests any obvious issues or optimizations

Be specific with numbers and trends. Focus on actionable insights."""

        try:
            interpretation = generate_text(prompt, max_tokens=300)
            return interpretation.strip()

        except Exception as e:
            logger.error(f"Error generating interpretation: {str(e)}")
            return ""
