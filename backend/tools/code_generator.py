"""
Code Generation Tools - Generate Python trading bot code from strategies

Uses Claude to generate clean, production-ready trading bot code
"""

import logging
import json
import ast
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from pydantic import ValidationError
from config import settings
from schemas.strategy import StrategySchema, validate_strategy

logger = logging.getLogger(__name__)

# Initialize Claude client
client = Anthropic(api_key=settings.anthropic_api_key)


def parse_strategy(strategy_description: str) -> Dict[str, Any]:
    """
    Parse natural language strategy into structured format

    Args:
        strategy_description: Plain English strategy description

    Returns:
        Structured strategy parameters
    """
    try:
        logger.info(f"📋 Parsing strategy: '{strategy_description[:100]}...'")

        prompt = f"""You are a quantitative trading expert. Parse this trading strategy into structured JSON format.

Strategy: "{strategy_description}"

Extract and return JSON with this structure:
{{
    "name": "descriptive strategy name",
    "description": "brief summary",
    "asset": "stock ticker (e.g., TSLA, AAPL) OR list of tickers for portfolio",
    "assets": ["TSLA", "AAPL", "NVDA"],  // Use for multi-stock portfolios, null for single stock
    "portfolio_mode": false,  // true if strategy trades multiple stocks as portfolio
    "entry_conditions": {{
        "signal": "rsi|macd|sma|sentiment|news|price",
        "description": "exact description of what triggers entry",
        "parameters": {{
            "rsi_threshold": 30,
            "rsi_exit_threshold": 70,
            "sma_short": 20,
            "sma_long": 50,
            "source": "twitter|reddit",
            "threshold": 0.1  // Use realistic sentiment threshold (typically -0.3 to +0.3)
        }}
    }},
    "exit_conditions": {{
        "take_profit": 0.02,
        "stop_loss": 0.01,
        "take_profit_pct_shares": 1.0,  // Percentage of position to sell when take profit hit (0.0-1.0, default 1.0 = 100%)
        "stop_loss_pct_shares": 1.0,  // Percentage of position to sell when stop loss hit (0.0-1.0, default 1.0 = 100%)
        "custom_exit": "description of custom exit condition if specified"
    }},
    "risk_management": {{
        "position_size": 1.0,
        "max_positions": 1,  // For portfolios, set to number of stocks or "dynamic" for trending
        "allocation": "equal",  // equal, signal_weighted, dynamic_trending, market_cap_weighted
        "dynamic_selection": false,  // true if stocks should be selected dynamically based on trending/signal strength
        "top_n": null  // For dynamic selection, how many top trending stocks to select
    }},
    "data_sources": ["twitter", "reddit", "news", "price", "rsi", "macd", "sma"]
}}

CRITICAL PARSING RULES:
1. Multi-Stock Detection:
   - "portfolio", "multiple stocks", "several stocks" → portfolio_mode: true, set assets list
   - "TSLA, AAPL, NVDA" or "TSLA and AAPL" → portfolio_mode: true, assets: ["TSLA", "AAPL", "NVDA"]
   - If portfolio_mode true, set max_positions to number of stocks in assets list
   - Single stock → portfolio_mode: false, asset: "TICKER", assets: null

2. Signal Type Detection:
   - "RSI" → signal: "rsi"
   - "MACD" → signal: "macd"
   - "moving average" or "SMA" → signal: "sma"
   - "tweet", "twitter", "social media", "Elon" → signal: "sentiment", source: "twitter"
   - "reddit", "wallstreetbets" → signal: "sentiment", source: "reddit"
   - "news", "announcement" → signal: "news"

3. Exit Conditions - CRITICAL:
   - If user specifies custom exit indicator (e.g., "sell when RSI > 70", "sell when MACD crosses"), set custom_exit and DO NOT include take_profit/stop_loss
   - ONLY include take_profit/stop_loss if user explicitly mentions percentages (e.g., "+2% profit", "-1% stop loss")
   - If user only mentions custom exit without TP/SL, set take_profit: null, stop_loss: null
   - ALWAYS extract partial exit percentages: "sell 50% at profit" → take_profit_pct_shares: 0.5
   - If user doesn't specify percentage of shares to sell, default to 1.0 (100%)
   - CRITICAL: For RSI mean-reversion with "sell half" or "partial exit" AND trailing stop, ALWAYS set take_profit_pct_shares: 0.5
   - CRITICAL: stop_loss values must be DECIMALS (0.10 for 10%), NOT percentages (10.0)

4. Examples:
   - "Sell when RSI > 70" → custom_exit: "RSI above 70", take_profit: null, stop_loss: null
   - "Sell at +2% profit or -1% stop loss" → take_profit: 0.02, stop_loss: 0.01, custom_exit: null
   - "Sell when RSI > 70 or at -1% stop loss" → custom_exit: "RSI above 70", stop_loss: 0.01, take_profit: null
   - "Sell 50% at +10% profit" → take_profit: 0.10, take_profit_pct_shares: 0.5
   - "Sell half when profit target hit" → take_profit_pct_shares: 0.5
   - "Buy RSI < 30, sell 50% when RSI > 70, use 10% trailing stop" → custom_exit: "RSI above 70", take_profit_pct_shares: 0.5, stop_loss: 0.10, stop_loss_pct_shares: 1.0

5. Portfolio Examples:
   - "Trade TSLA, AAPL, NVDA based on RSI" → portfolio_mode: true, assets: ["TSLA", "AAPL", "NVDA"], max_positions: 3, allocation: "equal"
   - "Create a portfolio of GME and AMC based on WSB sentiment" → portfolio_mode: true, assets: ["GME", "AMC"], max_positions: 2, signal: "sentiment", source: "reddit", allocation: "equal"
   - "Buy BYND when sentiment positive" → portfolio_mode: false, asset: "BYND", assets: null, max_positions: 1

6. Dynamic Allocation Detection:
   - "trending stocks", "most mentioned", "top stocks" → dynamic_selection: true, assets: null
   - "trending on wallstreetbets" → dynamic_selection: true, source: "reddit", assets: null
   - "allocate more to stocks with higher sentiment" → allocation: "signal_weighted"
   - "weight by sentiment strength" → allocation: "signal_weighted"
   - If dynamic_selection is true, set assets: null (stocks will be selected at runtime)

7. Dynamic Portfolio Examples:
   - "Trade the top 5 trending stocks on wallstreetbets" → portfolio_mode: true, dynamic_selection: true, top_n: 5, source: "reddit", assets: null, allocation: "signal_weighted"
   - "Create a portfolio of trending WSB stocks, allocate more to higher sentiment" → portfolio_mode: true, dynamic_selection: true, allocation: "signal_weighted", source: "reddit"
   - "Trade top 3 stocks with highest Reddit mentions" → portfolio_mode: true, dynamic_selection: true, top_n: 3, source: "reddit", allocation: "signal_weighted"

Return ONLY valid JSON, no other text."""

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to find JSON in the response
        json_start = content.find("{")
        json_end = content.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = content[json_start:json_end]
            parsed = json.loads(json_str)

            logger.info(f"✅ Parsed strategy: {parsed.get('name', 'Unknown')}")
            logger.info(f"   Asset: {parsed.get('asset')}")
            logger.info(f"   Data sources: {parsed.get('data_sources')}")

            # Validate and normalize through schema
            try:
                validated_strategy = validate_strategy(parsed)
                logger.info(f"✅ Schema validation passed")
                logger.info(f"   {validated_strategy.get_summary()}")

                # Log normalization details for debugging
                if validated_strategy.exit_conditions.stop_loss is not None:
                    logger.info(f"   Stop Loss (normalized): {validated_strategy.exit_conditions.stop_loss:.4f} ({validated_strategy.exit_conditions.stop_loss*100:.1f}%)")
                if validated_strategy.exit_conditions.take_profit is not None:
                    logger.info(f"   Take Profit (normalized): {validated_strategy.exit_conditions.take_profit:.4f} ({validated_strategy.exit_conditions.take_profit*100:.1f}%)")
                if validated_strategy.exit_conditions.take_profit_pct_shares < 1.0:
                    logger.info(f"   Partial Exit: {validated_strategy.exit_conditions.take_profit_pct_shares*100:.0f}% at take profit")
                if validated_strategy.is_two_phase_exit:
                    logger.info(f"   ✅ Two-phase exit mode detected (partial exit + trailing stop)")

                # Convert back to dict for compatibility
                parsed = validated_strategy.to_dict()

            except ValidationError as e:
                logger.warning(f"⚠️  Schema validation failed: {e}")
                logger.warning("   Proceeding with raw parsed strategy")

            # Check if strategy requires dynamic selection without specific assets
            if parsed.get('dynamic_selection') and not parsed.get('asset') and not parsed.get('assets'):
                logger.error(f"   ❌ Strategy requires dynamic trending stock selection")
                return {
                    "success": False,
                    "error": "This strategy requires real-time trending stock data from Reddit. Backtesting is not available for dynamic trending strategies because historical trending data is not accessible. For backtesting, please specify exact stock symbols (e.g., 'Trade GME and AMC based on Reddit sentiment'). For live trading with trending stocks, deploy the bot directly.",
                    "strategy": parsed
                }

            return {
                "success": True,
                "strategy": parsed,
            }
        else:
            raise ValueError("No valid JSON found in response")

    except Exception as e:
        logger.error(f"❌ Error parsing strategy: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def generate_trading_bot_code(
    strategy: Dict[str, Any], include_backtest: bool = False
) -> Dict[str, Any]:
    """
    Generate Python trading bot code from parsed strategy

    Args:
        strategy: Parsed strategy parameters
        include_backtest: Whether to include backtesting code

    Returns:
        Generated Python code
    """
    try:
        logger.info(f"🤖 Generating code for strategy: {strategy.get('name')}")

        # Build prompt for code generation
        prompt = f"""You are an expert Python developer specializing in algorithmic trading.

Generate a complete, production-ready Python trading bot based on this strategy:

{json.dumps(strategy, indent=2)}

Requirements:
1. Use the Alpaca API for trading (alpaca-py library)
2. Include all necessary imports
3. Implement entry and exit logic based on strategy
4. Add proper error handling
5. Include logging
6. Calculate position sizes correctly
7. Implement stop loss and take profit
8. Add docstrings and comments
9. Make it executable

**CRITICAL - Data Validation:**
10. ALWAYS check for None/null values before comparisons or mathematical operations
11. Skip iterations if RSI, sentiment, or any indicator returns None
12. Use patterns like: `if rsi is not None and rsi < 30:` instead of `if rsi < 30:`
13. Handle missing data gracefully with continue statements
14. Never compare None with numbers - this will crash the backtest

**CRITICAL - TWO-PHASE EXIT LOGIC FOR PARTIAL EXITS AND TRAILING STOPS:**

When a strategy involves partial exits (e.g., "sell 50% when RSI > 70") combined with trailing stops, you MUST implement the following two-phase exit flow:

PHASE 1 - Full Position (before partial exit):
- NO trailing stop is active yet
- Only exit trigger is the RSI threshold (or other indicator-based exit)
- When RSI crosses above threshold, sell EXACTLY the specified percentage (e.g., 50%)
- Store the ORIGINAL position size at entry to calculate exact exit quantity
- Mark partial_exit_done = True to prevent repeated partial exits

PHASE 2 - Remaining Position (after partial exit):
- Trailing stop is NOW activated
- Initialize trailing stop based on current price AFTER partial exit, NOT entry price
- Track highest_price_since_partial_exit (reset when partial exit happens)
- Trailing stop price = highest_price_since_partial_exit * (1 - trailing_stop_pct)
- Only the trailing stop can trigger exit in this phase
- When trailing stop hits, exit ALL remaining shares

STATE VARIABLES REQUIRED:
```python
self.entry_price = None              # Original entry price
self.original_shares = None          # Shares at entry (for calculating 50%)
self.partial_exit_done = False       # Flag to prevent multiple partial exits
self.trailing_stop_active = False    # Only True AFTER partial exit
self.highest_price_since_partial_exit = None  # For trailing stop calculation
self.trailing_stop_price = None      # Current trailing stop level
```

CRITICAL RULES:
1. partial_exit_done prevents repeated 50% exits (50 -> 25 -> 12 is WRONG)
2. Calculate exit_qty from ORIGINAL position: `exit_qty = int(self.original_shares * 0.5)`
3. Trailing stop ONLY activates after partial exit happens
4. After partial exit, reset highest price tracker to current price
5. Never use position_qty // 2 repeatedly - that causes cascading exits

CORRECT check_exit_conditions() LOGIC:
```python
def check_exit_conditions(self, position) -> dict:
    result = {{'should_exit': False, 'quantity': 0, 'reason': None}}

    if position is None:
        return result

    current_price = self.get_current_price()
    current_rsi = self.get_current_rsi()
    position_qty = int(float(position.qty))

    if current_price is None or current_rsi is None:
        return result

    # Initialize tracking on first check
    if self.original_shares is None:
        self.original_shares = position_qty
        self.entry_price = float(position.avg_entry_price)

    # PHASE 1: Partial exit on RSI signal (only once!)
    if not self.partial_exit_done and current_rsi > self.rsi_sell_threshold:
        exit_qty = int(self.original_shares * 0.5)  # Use ORIGINAL, not current
        exit_qty = min(exit_qty, position_qty)  # Safety check

        result['should_exit'] = True
        result['quantity'] = exit_qty
        result['reason'] = f"Partial exit: RSI ({{current_rsi:.2f}}) > {{self.rsi_sell_threshold}}"
        return result

    # PHASE 2: Trailing stop (only after partial exit)
    if self.partial_exit_done and self.trailing_stop_active:
        # Update highest price and trailing stop
        if current_price > self.highest_price_since_partial_exit:
            self.highest_price_since_partial_exit = current_price
            self.trailing_stop_price = current_price * (1 - self.trailing_stop_pct)

        # Check if trailing stop hit
        if current_price <= self.trailing_stop_price:
            result['should_exit'] = True
            result['quantity'] = position_qty  # All remaining shares
            result['reason'] = f"Trailing stop: ${{current_price:.2f}} <= ${{self.trailing_stop_price:.2f}}"
            return result

    return result
```

CORRECT execute_sell() STATE UPDATE:
```python
def execute_sell(self, quantity: int, reason: str):
    # ... order execution code ...

    # Update state after successful sell
    remaining_position = self.get_position()

    if remaining_position is None or int(float(remaining_position.qty)) == 0:
        # Fully exited - reset all state
        self._reset_position_state()
    elif "Partial exit" in reason and not self.partial_exit_done:
        # First partial exit just happened - activate trailing stop
        self.partial_exit_done = True
        self.trailing_stop_active = True
        current_price = self.get_current_price()
        self.highest_price_since_partial_exit = current_price
        self.trailing_stop_price = current_price * (1 - self.trailing_stop_pct)
        logger.info(f"🎯 Trailing stop activated at ${{self.trailing_stop_price:.2f}}")

def _reset_position_state(self):
    self.entry_price = None
    self.original_shares = None
    self.partial_exit_done = False
    self.trailing_stop_active = False
    self.highest_price_since_partial_exit = None
    self.trailing_stop_price = None
```

Structure:
```python
import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from datetime import datetime
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        \"\"\"Initialize the trading bot\"\"\"
        self.client = TradingClient(api_key, secret_key, paper=paper)
        self.symbol = "{strategy.get('asset', 'AAPL')}"
        # Add strategy parameters...

    def check_entry_conditions(self) -> bool:
        \"\"\"Check if entry conditions are met\"\"\"
        # Implement entry logic based on strategy
        pass

    def check_exit_conditions(self, position) -> bool:
        \"\"\"Check if exit conditions are met\"\"\"
        # Implement exit logic (take profit, stop loss)
        pass

    def execute_trade(self, action: str):
        \"\"\"Execute buy or sell trade\"\"\"
        # Implement trading logic
        pass

    def run(self):
        \"\"\"Main trading loop\"\"\"
        logger.info(f"🚀 Starting {{self.symbol}} trading bot")

        while True:
            try:
                # Check conditions and execute trades
                pass
            except Exception as e:
                logger.error(f"Error: {{e}}")

            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    # Initialize with your API keys
    bot = TradingBot(
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY",
        paper=True
    )
    bot.run()
```

Generate the COMPLETE, working code. Include all logic for:
- {strategy.get('data_sources', [])} data sources
- Entry conditions: {strategy.get('entry_conditions', [])}
- Exit conditions: {strategy.get('exit_conditions', {})}

Make it copy-paste ready!"""

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract code from response
        content = response.content[0].text

        # Try to extract code blocks
        if "```python" in content:
            code_start = content.find("```python") + 9
            code_end = content.find("```", code_start)
            code = content[code_start:code_end].strip()
        elif "```" in content:
            code_start = content.find("```") + 3
            code_end = content.find("```", code_start)
            code = content[code_start:code_end].strip()
        else:
            code = content

        # Validate the code (syntax check)
        try:
            ast.parse(code)
            logger.info("✅ Generated code is syntactically valid")
            is_valid = True
        except SyntaxError as e:
            logger.warning(f"⚠️  Generated code has syntax error: {e}")
            is_valid = False

        logger.info(f"✅ Generated {len(code)} characters of code")

        return {
            "success": True,
            "code": code,
            "is_valid": is_valid,
            "lines": len(code.split("\n")),
            "strategy_name": strategy.get("name"),
        }

    except Exception as e:
        logger.error(f"❌ Error generating code: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def create_trading_strategy(strategy_description: str) -> Dict[str, Any]:
    """
    Complete pipeline: Parse strategy and generate code

    Args:
        strategy_description: Plain English strategy

    Returns:
        Parsed strategy + generated code
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Creating trading strategy from description:")
    logger.info(f"   '{strategy_description}'")
    logger.info(f"{'='*60}\n")

    # Step 1: Parse strategy
    parsed = parse_strategy(strategy_description)

    if not parsed["success"]:
        return parsed

    strategy = parsed["strategy"]

    # Step 2: Generate code
    code_result = generate_trading_bot_code(strategy)

    if not code_result["success"]:
        return code_result

    # Combine results
    return {
        "success": True,
        "strategy": strategy,
        "code": code_result["code"],
        "is_valid": code_result["is_valid"],
        "lines_of_code": code_result["lines"],
        "message": f"✅ Successfully created '{strategy['name']}' trading bot with {code_result['lines']} lines of code",
    }


def validate_trading_code(code: str) -> Dict[str, Any]:
    """
    Validate generated trading code

    Args:
        code: Python code to validate

    Returns:
        Validation results
    """
    try:
        # Check syntax
        ast.parse(code)

        # Check for required components
        has_class = "class" in code and "TradingBot" in code
        has_init = "__init__" in code
        has_entry_check = "entry" in code.lower()
        has_exit_check = "exit" in code.lower()
        has_execute = "execute" in code.lower()
        has_run = "def run" in code

        checks = {
            "valid_syntax": True,
            "has_trading_class": has_class,
            "has_initialization": has_init,
            "has_entry_logic": has_entry_check,
            "has_exit_logic": has_exit_check,
            "has_execution": has_execute,
            "has_main_loop": has_run,
        }

        all_passed = all(checks.values())

        return {
            "success": True,
            "valid": all_passed,
            "checks": checks,
            "message": "✅ All checks passed" if all_passed else "⚠️  Some checks failed",
        }

    except SyntaxError as e:
        return {
            "success": False,
            "valid": False,
            "error": f"Syntax error: {e}",
        }


# Tool schemas for Claude
CODE_GENERATION_TOOLS = [
    {
        "name": "parse_strategy",
        "description": "Parse a natural language trading strategy into structured format. Extracts asset, entry/exit conditions, risk parameters, and required data sources.",
        "input_schema": {
            "type": "object",
            "properties": {
                "strategy_description": {
                    "type": "string",
                    "description": "Plain English description of the trading strategy",
                }
            },
            "required": ["strategy_description"],
        },
    },
    {
        "name": "generate_trading_bot_code",
        "description": "Generate complete Python trading bot code from a parsed strategy. Creates production-ready code with entry/exit logic, risk management, and Alpaca API integration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "object",
                    "description": "Parsed strategy object (from parse_strategy)",
                },
                "include_backtest": {
                    "type": "boolean",
                    "description": "Whether to include backtesting code (default: false)",
                    "default": False,
                },
            },
            "required": ["strategy"],
        },
    },
    {
        "name": "create_trading_strategy",
        "description": "Complete end-to-end: Parse natural language strategy AND generate Python code in one step. Use this for the full strategy-to-code pipeline.",
        "input_schema": {
            "type": "object",
            "properties": {
                "strategy_description": {
                    "type": "string",
                    "description": "Plain English trading strategy description",
                }
            },
            "required": ["strategy_description"],
        },
    },
]
