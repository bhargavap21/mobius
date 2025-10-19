"""
Unified LLM client wrapper for Anthropic API

This module provides a simple interface for making LLM calls
that abstracts away the specific API details.
"""

import json
import logging
import traceback
import anthropic
from config import settings

logger = logging.getLogger(__name__)

# Configure Anthropic client
anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


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
