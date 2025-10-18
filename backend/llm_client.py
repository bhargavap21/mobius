"""
Unified LLM client wrapper for Gemini API

This module provides a simple interface for making LLM calls
that abstracts away the specific API details.
"""

import json
import logging
import traceback
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


def generate_text(prompt: str, system_instruction: str = None, max_tokens: int = 4000, model: str = None) -> str:
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
        # Use configured model if not specified
        if model is None:
            model = settings.gemini_model

        # Log API key being used (first 10 chars for security)
        api_key_preview = settings.gemini_api_key[:10] + "..." if settings.gemini_api_key else "NONE"
        logger.info(f"🔑 Using API key: {api_key_preview}")
        logger.info(f"🤖 Using model: {model}")
        logger.info(f"📏 Prompt size: {len(prompt)} chars, System instruction: {len(system_instruction) if system_instruction else 0} chars")

        # Create model with system instruction if provided
        if system_instruction:
            model_instance = genai.GenerativeModel(
                model,
                system_instruction=system_instruction
            )
        else:
            model_instance = genai.GenerativeModel(model)

        # Generate response
        # NOTE: Removed max_output_tokens due to gemini-2.5-flash bug where it returns empty content
        # when max_output_tokens is set, even with reasonable values like 2000-4000
        response = model_instance.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                # max_output_tokens=max_tokens,  # Disabled - causes finish_reason=2 with empty content
                temperature=0.7,
            )
        )

        # Access the text from the response
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]

            # Log detailed response structure for debugging
            logger.info(f"🔍 Gemini Response Debug:")
            logger.info(f"  - Has candidate: True")
            logger.info(f"  - Finish reason: {candidate.finish_reason}")
            logger.info(f"  - Has content: {candidate.content is not None}")
            if hasattr(candidate, 'safety_ratings'):
                logger.info(f"  - Safety ratings: {candidate.safety_ratings}")

            # Check if blocked by safety filters
            if candidate.finish_reason == 3:  # SAFETY
                logger.error(f"❌ Response blocked by safety filters!")
                logger.error(f"Safety ratings: {candidate.safety_ratings}")
                raise ValueError("Response blocked by Gemini safety filters")

            if candidate.content and candidate.content.parts and len(candidate.content.parts) > 0:
                return candidate.content.parts[0].text
            else:
                logger.error(f"❌ Empty response - candidate.content: {candidate.content}")
                logger.error(f"Full candidate: {candidate}")
                raise ValueError("No content in Gemini response (empty parts)")
        else:
            raise ValueError("No response generated from Gemini (no candidates)")

    except Exception as e:
        logger.error(f"Error generating text with Gemini: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
