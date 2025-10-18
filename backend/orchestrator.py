"""
Claude AI Orchestrator - The Brain of the Trading Bot

This module handles:
1. Natural language understanding
2. Tool selection and execution
3. Multi-step reasoning
4. Response generation
"""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
import google.generativeai as genai
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingBotOrchestrator:
    """
    Main orchestrator that uses Gemini to understand requests and coordinate tools
    """

    def __init__(self):
        """Initialize the orchestrator with Gemini client and tool registry"""
        genai.configure(api_key=settings.gemini_api_key)
        self.client = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        function: Callable,
    ):
        """
        Register a tool that Claude can use

        Args:
            name: Tool name (e.g., "get_stock_price")
            description: What the tool does
            input_schema: JSON schema for tool parameters
            function: Python function to execute
        """
        # Store the function
        self.tools[name] = function

        # Store the schema for Claude
        tool_schema = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
        }
        self.tool_schemas.append(tool_schema)

        logger.info(f"✅ Registered tool: {name}")

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Execute a registered tool

        Args:
            tool_name: Name of the tool to execute
            tool_input: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        logger.info(f"🔧 Executing tool: {tool_name}")
        logger.debug(f"   Input: {tool_input}")

        try:
            result = self.tools[tool_name](**tool_input)
            logger.info(f"✅ Tool '{tool_name}' completed")
            return result
        except Exception as e:
            logger.error(f"❌ Tool '{tool_name}' failed: {e}")
            return {"error": str(e), "tool": tool_name}

    def create_trading_bot(
        self, user_strategy: str, max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Main entry point: Create a trading bot from natural language

        Args:
            user_strategy: User's strategy in plain English
            max_iterations: Max tool calls to prevent infinite loops

        Returns:
            Complete result with strategy, code, backtest, etc.
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Creating trading bot from strategy:")
        logger.info(f"   '{user_strategy}'")
        logger.info(f"{'='*60}\n")

        system_prompt = """You are an expert trading strategy architect and Python developer.

Your job is to help users create, backtest, and deploy trading strategies.

When a user describes a trading strategy:
1. Parse and understand their intent
2. Identify what data sources are needed
3. Use available tools to gather data
4. Generate Python trading bot code
5. Backtest the strategy
6. Analyze results and suggest improvements

Be concise but thorough. Use tools to accomplish tasks rather than just describing them.
When you have a complete answer, provide it clearly."""

        messages = [{"role": "user", "content": user_strategy}]

        iterations = 0
        final_response = None

        while iterations < max_iterations:
            iterations += 1
            logger.info(f"🔄 Iteration {iterations}/{max_iterations}")

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    tools=self.tool_schemas if self.tool_schemas else None,
                    messages=messages,
                )

                logger.debug(f"Claude response: {response.stop_reason}")

                # Add assistant's response to conversation
                messages.append({"role": "assistant", "content": response.content})

                # Check if Claude wants to use a tool
                if response.stop_reason == "tool_use":
                    # Find all tool use blocks
                    tool_uses = [
                        block for block in response.content if block.type == "tool_use"
                    ]

                    tool_results = []
                    for tool_use in tool_uses:
                        logger.info(f"🔧 Claude wants to use: {tool_use.name}")

                        # Execute the tool
                        result = self.execute_tool(tool_use.name, tool_use.input)

                        # Format result for Claude
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": json.dumps(result, default=str),
                            }
                        )

                    # Send tool results back to Claude
                    messages.append({"role": "user", "content": tool_results})

                elif response.stop_reason == "end_turn":
                    # Claude is done!
                    logger.info("✅ Claude finished processing")

                    # Extract text response
                    text_blocks = [
                        block.text
                        for block in response.content
                        if hasattr(block, "text")
                    ]
                    final_response = "\n".join(text_blocks)
                    break

                else:
                    # Unexpected stop reason
                    logger.warning(f"⚠️  Unexpected stop reason: {response.stop_reason}")
                    break

            except Exception as e:
                logger.error(f"❌ Error during orchestration: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "iterations": iterations,
                }

        if iterations >= max_iterations:
            logger.warning("⚠️  Reached max iterations")

        return {
            "success": True,
            "response": final_response,
            "iterations": iterations,
            "conversation": messages,
        }

    def chat(
        self, user_message: str, conversation_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Simple chat interface for testing

        Args:
            user_message: User's message
            conversation_history: Previous messages (optional)

        Returns:
            Response and updated conversation
        """
        if conversation_history is None:
            conversation_history = []

        conversation_history.append({"role": "user", "content": user_message})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                tools=self.tool_schemas if self.tool_schemas else None,
                messages=conversation_history,
            )

            # Handle tool use
            if response.stop_reason == "tool_use":
                conversation_history.append(
                    {"role": "assistant", "content": response.content}
                )

                tool_uses = [
                    block for block in response.content if block.type == "tool_use"
                ]
                tool_results = []

                for tool_use in tool_uses:
                    result = self.execute_tool(tool_use.name, tool_use.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": json.dumps(result, default=str),
                        }
                    )

                conversation_history.append({"role": "user", "content": tool_results})

                # Get final response
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    messages=conversation_history,
                )

            # Extract text
            text_blocks = [
                block.text for block in response.content if hasattr(block, "text")
            ]
            response_text = "\n".join(text_blocks)

            conversation_history.append({"role": "assistant", "content": response_text})

            return {
                "success": True,
                "response": response_text,
                "conversation": conversation_history,
            }

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {"success": False, "error": str(e)}


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> TradingBotOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TradingBotOrchestrator()
    return _orchestrator
