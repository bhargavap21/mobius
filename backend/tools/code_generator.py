"""
Code Generation Tools - Generate Python trading bot code from strategies

Uses Gemini to generate clean, production-ready trading bot code
"""

import logging
import json
import ast
from typing import Dict, List, Any, Optional
from llm_client import generate_json, generate_text

logger = logging.getLogger(__name__)


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
    "asset": "stock ticker (e.g., TSLA, AAPL)",
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
        "custom_exit": "description of custom exit condition if specified"
    }},
    "risk_management": {{
        "position_size": 1.0,
        "max_positions": 1
    }},
    "data_sources": ["twitter", "reddit", "news", "price", "rsi", "macd", "sma"]
}}

CRITICAL PARSING RULES:
1. Signal Type Detection:
   - "RSI" → signal: "rsi"
   - "MACD" → signal: "macd"
   - "moving average" or "SMA" → signal: "sma"
   - "tweet", "twitter", "social media", "Elon" → signal: "sentiment", source: "twitter"
   - "reddit", "wallstreetbets" → signal: "sentiment", source: "reddit"
   - "news", "announcement" → signal: "news"

2. Exit Conditions - CRITICAL:
   - If user specifies custom exit indicator (e.g., "sell when RSI > 70", "sell when MACD crosses"), set custom_exit and DO NOT include take_profit/stop_loss
   - ONLY include take_profit/stop_loss if user explicitly mentions percentages (e.g., "+2% profit", "-1% stop loss")
   - If user only mentions custom exit without TP/SL, set take_profit: null, stop_loss: null

3. Examples:
   - "Sell when RSI > 70" → custom_exit: "RSI above 70", take_profit: null, stop_loss: null
   - "Sell at +2% profit or -1% stop loss" → take_profit: 0.02, stop_loss: 0.01, custom_exit: null
   - "Sell when RSI > 70 or at -1% stop loss" → custom_exit: "RSI above 70", stop_loss: 0.01, take_profit: null

Return ONLY valid JSON, no other text."""

        parsed = generate_json(prompt, max_tokens=2000)

        logger.info(f"✅ Parsed strategy: {parsed['name']}")
        logger.info(f"   Asset: {parsed.get('asset')}")
        logger.info(f"   Data sources: {parsed.get('data_sources')}")

        return {
            "success": True,
            "strategy": parsed,
        }

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

        content = generate_text(prompt, max_tokens=4096)

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
