"""
Unified LLM client wrapper for Anthropic and Gemini APIs

This module provides a simple interface for making LLM calls
that abstracts away the specific API details.
"""

import json
import logging
import traceback
import anthropic
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Configure Anthropic client
anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Configure Gemini client
genai.configure(api_key=settings.gemini_api_key)


def generate_text(prompt: str, system_instruction: str = None, max_tokens: int = 4000, model: str = None) -> str:
    """
    Generate text using Anthropic API

    Args:
        prompt: The user prompt/question
        system_instruction: Optional system instruction to guide the model
        max_tokens: Maximum tokens in response
        model: Model to use

    Returns:
        Generated text response
    """
    try:
        # Use configured model if not specified
        if model is None:
            model = settings.anthropic_model

        # Log API key being used (first 10 chars for security)
        api_key_preview = settings.anthropic_api_key[:10] + "..." if settings.anthropic_api_key else "NONE"
        logger.info(f"🔑 Using API key: {api_key_preview}")
        logger.info(f"🤖 Using model: {model}")
        logger.info(f"📏 Prompt size: {len(prompt)} chars, System instruction: {len(system_instruction) if system_instruction else 0} chars")

        # Prepare messages for Anthropic
        messages = [{"role": "user", "content": prompt}]
        
        # Generate response using Anthropic
        # Handle system instruction properly - don't pass None
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": 0.7
        }
        
        # Only add system if it's provided and not None
        if system_instruction:
            kwargs["system"] = system_instruction
            
        response = anthropic_client.messages.create(**kwargs)

        # Extract text from response
        if response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            logger.error(f"❌ Empty response from Anthropic: {response}")
            raise ValueError("No content in Anthropic response")

    except Exception as e:
        logger.error(f"Error generating text with Anthropic: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


def generate_json(prompt: str, system_instruction: str = None, max_tokens: int = 4000) -> dict:
    """
    Generate JSON response using Anthropic API

    Args:
        prompt: The user prompt/question
        system_instruction: Optional system instruction
        max_tokens: Maximum tokens in response

    Returns:
        Parsed JSON response
    """
    try:
        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nReturn ONLY valid JSON, no other text."

        text_response = generate_text(json_prompt, system_instruction, max_tokens)

        # Extract JSON from response
        json_start = text_response.find("{")
        json_end = text_response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = text_response[json_start:json_end]
            return json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")

    except Exception as e:
        logger.error(f"Error generating JSON with Anthropic: {e}")
        raise


def generate_gemini_chat(user_message: str, context: dict = None) -> str:
    """
    Generate chat response using Gemini API with full context

    Args:
        user_message: The user's question
        context: Full backtest context including strategy, results, trades, etc.

    Returns:
        Gemini's response
    """
    try:
        # Build comprehensive context prompt
        context_str = ""
        if context:
            context_str = f"""
You are analyzing a trading strategy with the following context:

STRATEGY DETAILS:
- Name: {context.get('name', 'N/A')}
- Asset: {context.get('asset', 'N/A')}
- Strategy Type: {context.get('strategy_type', 'N/A')}

BACKTEST RESULTS:
{json.dumps(context.get('backtest_results', {}), indent=2)}

STRATEGY PARAMETERS:
{json.dumps(context.get('parameters', {}), indent=2)}

Please provide actionable insights and answer the user's question based on this data.
"""

        # Combine context with user message
        full_prompt = f"{context_str}\n\nUSER QUESTION: {user_message}"

        # Use Gemini
        model = genai.GenerativeModel(settings.gemini_model)
        response = model.generate_content(full_prompt)

        return response.text

    except Exception as e:
        logger.error(f"Error generating Gemini chat response: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise
