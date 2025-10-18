"""
Strategy Analyst Agent - Reviews backtest results and provides feedback
"""
import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent
from orchestrator import get_orchestrator

logger = logging.getLogger(__name__)


class StrategyAnalystAgent(BaseAgent):
    """
    Analyzes backtest results and provides feedback for improvement

    Responsibilities:
    - Review backtest metrics (trades, returns, win rate)
    - Identify issues (too few trades, poor performance, etc.)
    - Suggest improvements (adjust timeframe, tweak parameters, change indicators)
    - Validate strategy viability
    """

    def __init__(self):
        super().__init__("StrategyAnalyst")
        self.orchestrator = get_orchestrator()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze backtest results and provide feedback

        Args:
            input_data: {
                'backtest_results': {...},
                'strategy': {...},
                'user_query': str,
                'iteration': int
            }

        Returns:
            {
                'success': bool,
                'analysis': str,
                'issues': list[str],
                'suggestions': list[str],
                'needs_refinement': bool,
                'should_continue': bool
            }
        """
        backtest_results = input_data.get('backtest_results', {})
        strategy = input_data.get('strategy', {})
        user_query = input_data.get('user_query', '')
        iteration = input_data.get('iteration', 1)

        summary = backtest_results.get('summary', {})

        # Build analysis prompt
        analysis_prompt = f"""You are a professional trading strategy analyst. Analyze this backtest result and provide detailed feedback.

USER'S ORIGINAL STRATEGY REQUEST:
{user_query}

STRATEGY CONFIGURATION:
- Asset: {strategy.get('asset', 'N/A')}
- Entry Conditions: {strategy.get('entry_conditions', {})}
- Exit Conditions: {strategy.get('exit_conditions', {})}

BACKTEST RESULTS (Iteration {iteration}):
- Symbol: {summary.get('symbol', 'N/A')}
- Timeframe: {summary.get('start_date', 'N/A')} to {summary.get('end_date', 'N/A')}
- Total Trades: {summary.get('total_trades', 0)}
- Win Rate: {summary.get('win_rate', 0)}%
- Total Return: {summary.get('total_return', 0)}%
- Buy & Hold Return: {summary.get('buy_hold_return', 0)}%
- Max Drawdown: {summary.get('max_drawdown', 0)}%
- Sharpe Ratio: {summary.get('sharpe_ratio', 0)}
- Profit Factor: {summary.get('profit_factor', 0)}
- External Data Found: {summary.get('external_data_found', 0)} days
- Data Points Checked: {summary.get('data_points_checked', 0)} days

CRITICAL ANALYSIS REQUIRED - BE SPECIFIC AND ACTIONABLE:

1. **ZERO TRADES DIAGNOSTIC (if total_trades = 0):**
   External data found: {summary.get('external_data_found', 0)}/{summary.get('data_points_checked', 0)} days

   IDENTIFY THE EXACT PROBLEM:
   a) Sentiment Strategy Issues:
      - If threshold > 0.3: Way too high! Real sentiment is -0.3 to +0.3
      - ACTION: Change sentiment threshold to 0.1 (not 0.5!)

   b) RSI Strategy Issues:
      - If using RSI < 30: Check if RSI actually goes below 30
      - ACTION: Use RSI < 35 for oversold, > 65 for overbought

   c) Volume Strategy Issues:
      - If using 3x volume: Too rare!
      - ACTION: Use 1.5x average volume

   d) Price Movement Issues:
      - If using > 5% daily move: Unrealistic for most stocks
      - ACTION: Use 2% daily move threshold

2. **Performance Analysis (if trades > 0):**
   - Win rate vs 40% target
   - Return vs buy & hold
   - Risk/reward ratio

3. **SPECIFIC REFINEMENT ACTIONS:**
   Based on the exact strategy type, provide EXACT parameter changes:
   - Don't say "adjust threshold" - say "change threshold from X to Y"
   - Don't say "consider different approach" - say "add RSI < 35 as additional filter"

RESPONSE FORMAT:

ANALYSIS: [One sentence summary]

ISSUES:
- [SPECIFIC issue with EXACT numbers]

SUGGESTIONS:
- [EXACT parameter change: "Set sentiment_threshold = 0.1"]
- [EXACT action: "Change RSI threshold from 30 to 35"]

NEEDS_REFINEMENT: YES (if 0 trades or poor performance)
SHOULD_CONTINUE: YES (unless iteration > 5)
"""

        # Use orchestrator to analyze
        result = self.orchestrator.chat(analysis_prompt)

        if not result.get('success'):
            return {
                'success': False,
                'error': 'Failed to analyze backtest results'
            }

        response_text = result.get('response', '')

        # Parse the response
        analysis = self._parse_response(response_text, summary)

        # Add to memory
        self.add_to_memory({
            'type': 'analysis',
            'iteration': iteration,
            'content': analysis
        })

        logger.info(f"Strategy analysis complete: {analysis['needs_refinement']=}, {analysis['should_continue']=}")

        return analysis

    def _parse_response(self, response: str, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Parse agent response into structured format"""
        lines = response.strip().split('\n')

        analysis_text = ""
        issues = []
        suggestions = []
        needs_refinement = True
        should_continue = True

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('ANALYSIS:'):
                current_section = 'analysis'
                analysis_text = line.replace('ANALYSIS:', '').strip()
            elif line.startswith('ISSUES:'):
                current_section = 'issues'
            elif line.startswith('SUGGESTIONS:'):
                current_section = 'suggestions'
            elif line.startswith('NEEDS_REFINEMENT:'):
                needs_refinement = 'YES' in line.upper()
                current_section = None
            elif line.startswith('SHOULD_CONTINUE:'):
                should_continue = 'YES' in line.upper()
                current_section = None
            elif line.startswith('-'):
                item = line.lstrip('- ').strip()
                if current_section == 'issues':
                    issues.append(item)
                elif current_section == 'suggestions':
                    suggestions.append(item)
            elif current_section == 'analysis':
                analysis_text += ' ' + line

        # Add automatic checks
        total_trades = summary.get('total_trades', 0)
        if total_trades < 3:
            if "Not enough trades executed" not in '\n'.join(issues):
                issues.insert(0, f"Not enough trades executed ({total_trades} trades) - strategy conditions may be too strict or timeframe too short")
                suggestions.insert(0, "Increase backtest timeframe to 360 days or relax entry conditions")
                needs_refinement = True

        return {
            'success': True,
            'analysis': analysis_text,
            'issues': issues,
            'suggestions': suggestions,
            'needs_refinement': needs_refinement,
            'should_continue': should_continue,
            'metrics': {
                'total_trades': summary.get('total_trades', 0),
                'win_rate': summary.get('win_rate', 0),
                'total_return': summary.get('total_return', 0),
                'sharpe_ratio': summary.get('sharpe_ratio', 0)
            }
        }
