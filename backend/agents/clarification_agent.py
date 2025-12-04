"""
Clarification Agent: Asks user clarifying questions before generating strategy
Focuses on parameters that would otherwise be assumed
"""

import logging
from anthropic import AsyncAnthropic
import os
import json

logger = logging.getLogger(__name__)

class ClarificationAgent:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    async def get_next_question(self, query: str = None, conversation_history: list = None):
        """
        Analyze query and conversation history to determine next clarifying question

        Returns:
            {
                "needs_clarification": bool,
                "question": str (if needs_clarification),
                "enriched_query": str (if not needs_clarification),
                "parameters": dict (extracted parameters)
            }
        """

        # Build prompt based on whether we have conversation history
        if not conversation_history or len(conversation_history) == 0:
            # First question - analyze initial query
            system_prompt = """You are a trading strategy clarification agent.

CRITICAL RULES:
1. You MUST first extract ALL parameters the user has ALREADY provided
2. You MUST NOT ask about parameters that are already specified
3. You ONLY ask about the SINGLE most important missing parameter

Required parameters for a trading strategy (in priority order):
- Asset/ticker: The stock/asset to trade
- Entry condition: When to buy (e.g., "RSI < 30")
- Take profit: When to exit with profit (e.g., "RSI > 70" or "5% gain")
- Stop loss: When to exit to limit loss (e.g., "1% loss")
- Take profit % shares: What percentage of position to sell when take profit hit (e.g., "sell 50%", "sell half") - REQUIRED, ask if not specified
- Stop loss % shares: What percentage of position to sell when stop loss hit (e.g., "sell 50%", "sell all") - REQUIRED, ask if not specified
- Backtest timeframe: How much historical data to test on (e.g., "60 days", "6 months", "1 year") - IMPORTANT: This is NOT how long to hold positions, but how far back in time to test the strategy
- Position sizing: How much to invest per trade

IMPORTANT: When user provides take profit or stop loss conditions, you MUST ask about partial exits if not specified. Most advanced strategies use partial exits (e.g., "sell 50% at profit, keep 50% running").

If ALL required parameters are provided, set needs_clarification=false."""

            user_prompt = f"""Query: "{query}"

First, extract what the user HAS provided:
- Asset: [extract if present]
- Entry condition: [extract if present]
- Take profit: [extract if present]
- Stop loss: [extract if present]
- Take profit % shares: [extract if present, e.g., "50%" = 0.5, "half" = 0.5, default 1.0 if not mentioned]
- Stop loss % shares: [extract if present, e.g., "50%" = 0.5, "all" = 1.0, default 1.0 if not mentioned]
- Position sizing: [extract if present]
- Backtest timeframe: [extract if present]

Then identify what is MISSING. If something critical is missing, ask about it. If everything is provided, set needs_clarification=false.

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "needs_clarification": true/false,
    "question": "your question" (only if needs_clarification=true),
    "enriched_query": "complete strategy" (only if needs_clarification=false),
    "parameters": {{"provided_param": "value"}}
}}

Example 1 - Missing exit:
Query: "Buy AAPL when RSI drops below 30"
Has: asset=AAPL, entry=RSI<30
Missing: take_profit, stop_loss, position_sizing
Response: {{"needs_clarification": true, "question": "What's your exit strategy? Do you want a take profit target (like when RSI goes above 70) and a stop loss (like -5%)?", "parameters": {{"asset": "AAPL", "entry": "RSI < 30"}}}}

Example 2 - Has stop/profit, missing partial exit %:
Query: "Buy META when RSI drops below 30. Sell when RSI goes above 70 or at -1% stop loss."
Has: asset=META, entry=RSI<30, take_profit=RSI>70, stop_loss=1%
Missing: take_profit_pct_shares, stop_loss_pct_shares
Response: {{"needs_clarification": true, "question": "When your take profit target (RSI > 70) is hit, do you want to sell your entire position (100%) or scale out partially? For example, you could sell 50% at the target and let the rest run.", "parameters": {{"asset": "META", "entry": "RSI < 30", "take_profit": "RSI > 70", "stop_loss": "1%"}}}}

Example 3 - Has exit conditions but missing partial exit percentage:
Query: "Buy TSLA when RSI < 30, sell at +5% profit or -2% loss"
Has: asset=TSLA, entry=RSI<30, take_profit=5%, stop_loss=2%
Missing: take_profit_pct_shares, stop_loss_pct_shares
Response: {{"needs_clarification": true, "question": "When you hit your +5% profit target, do you want to close the entire position or take partial profits? Many traders sell 50-75% and let the remainder run with a trailing stop.", "parameters": {{"asset": "TSLA", "entry": "RSI < 30", "take_profit": "5%", "stop_loss": "2%"}}}}

Example 4 - User specified partial exit:
Query: "Buy AMZN when RSI < 30, sell 50% when RSI > 70"
Has: asset=AMZN, entry=RSI<30, take_profit=RSI>70, take_profit_pct_shares=0.5
Missing: stop_loss, stop_loss_pct_shares
Response: {{"needs_clarification": true, "question": "What about a stop loss to limit downside risk? And if the stop loss is hit, do you want to exit the full position or just part of it?", "parameters": {{"asset": "AMZN", "entry": "RSI < 30", "take_profit": "RSI > 70", "take_profit_pct_shares": "0.5"}}}}

Example 5 - Everything provided including partial exits:
Query: "Buy SPY when RSI < 30, sell 50% when RSI > 70, full exit at -3% stop loss, backtest 6 months"
Has: asset=SPY, entry=RSI<30, take_profit=RSI>70, take_profit_pct_shares=0.5, stop_loss=3%, stop_loss_pct_shares=1.0, backtest_timeframe=6 months
Response: {{"needs_clarification": false, "enriched_query": "Buy SPY when RSI drops below 30, sell 50% of position when RSI goes above 70, full exit at -3% stop loss, backtest over 6 months", "parameters": {{"asset": "SPY", "entry": "RSI < 30", "take_profit": "RSI > 70", "take_profit_pct_shares": "0.5", "stop_loss": "3%", "stop_loss_pct_shares": "1.0", "backtest_timeframe": "6 months"}}}}"""

        else:
            # Follow-up question - analyze conversation so far
            system_prompt = """You are a trading strategy clarification agent. Continue asking clarifying questions ONE at a time until you have enough information to generate a complete trading strategy.

Key parameters to clarify:
1. Stop loss percentage
2. Take profit percentage
3. Position sizing strategy
4. Entry/exit thresholds
5. Time horizon
6. Risk management rules

Once you have enough information to create a solid strategy, set needs_clarification to false."""

            # Format conversation history
            conv_text = "\n".join([
                f"{'Assistant' if msg['role'] == 'assistant' else 'User'}: {msg['content']}"
                for msg in conversation_history
            ])

            user_prompt = f"""Analyze this conversation and respond with ONLY valid JSON (no markdown, no explanations):

Conversation so far:
{conv_text}

Determine if more clarification is needed, or if you have enough information to generate a complete trading strategy.

Respond with valid JSON only:
{{
    "needs_clarification": true/false,
    "question": "your next question" (only if needs_clarification is true),
    "enriched_query": "complete strategy description with all clarified parameters" (only if needs_clarification is false),
    "parameters": {{"key": "value"}} (all extracted parameters so far)
}}"""

        try:
            logger.info("🤔 Asking LLM for clarification...")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            content = response.content[0].text
            logger.info(f"📝 LLM FULL response:\n{content}")

            # Strip markdown code blocks if present
            original_content = content
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
                logger.info("Stripped '```json' prefix")
            if content.startswith("```"):
                content = content[3:]  # Remove ```
                logger.info("Stripped '```' prefix")
            if content.endswith("```"):
                content = content[:-3]  # Remove trailing ```
                logger.info("Stripped '```' suffix")
            content = content.strip()

            if content != original_content:
                logger.info(f"📝 After stripping markdown:\n{content}")

            # Parse JSON response
            try:
                result = json.loads(content)
                logger.info(f"✅ Successfully parsed JSON: needs_clarification={result.get('needs_clarification')}")
                return result
            except json.JSONDecodeError as json_err:
                logger.error(f"❌ JSON parsing failed: {json_err}")
                logger.error(f"❌ Content that failed to parse:\n{content}")
                raise

        except Exception as e:
            logger.error(f"❌ Error in clarification agent: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback:\n{traceback.format_exc()}")
            raise  # Re-raise instead of silently falling back
