"""
Unified LLM client wrapper for Gemini API

This module provides a simple interface for making LLM calls
that abstracts away the specific API details.
"""

import json
import logging
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


def generate_text(prompt: str, system_instruction: str = None, max_tokens: int = 4000, model: str = "gemini-2.0-flash-exp") -> str:
    """
    Generate text using Gemini API

    Args:
        prompt: The user prompt/question
        system_instruction: Optional system instruction to guide the model
        max_tokens: Maximum tokens in response
        model: Model to use

    Returns:
        Generated text response
    """
    try:
        # Create model with system instruction if provided
        if system_instruction:
            model_instance = genai.GenerativeModel(
                model,
                system_instruction=system_instruction
            )
        else:
            model_instance = genai.GenerativeModel(model)

        # Generate response
        response = model_instance.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )

        return response.text

    except Exception as e:
        logger.error(f"Error generating text with Gemini: {e}")
        raise


def generate_json(prompt: str, system_instruction: str = None, max_tokens: int = 4000) -> dict:
    """
    Generate JSON response using Gemini API

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
        logger.error(f"Error generating JSON with Gemini: {e}")
        raise
