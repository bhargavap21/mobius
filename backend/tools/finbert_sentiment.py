"""
FinBERT-based sentiment analysis for financial text
Uses ProsusAI/finbert pre-trained model for finance-specific sentiment
"""
import logging
from typing import Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

class FinBERTSentimentAnalyzer:
    """
    Sentiment analyzer using FinBERT model
    Returns sentiment scores from -1 (bearish) to +1 (bullish)
    """

    _instance = None
    _model = None
    _tokenizer = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern to load model only once"""
        if cls._instance is None:
            cls._instance = super(FinBERTSentimentAnalyzer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize FinBERT model (lazy loading)"""
        if not self._initialized:
            try:
                logger.info("📊 Loading FinBERT model (first time only)...")
                self._tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
                self._model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
                self._model.eval()  # Set to evaluation mode
                self._initialized = True
                logger.info("✅ FinBERT model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load FinBERT model: {e}")
                self._initialized = False

    def analyze(self, text: str) -> Optional[float]:
        """
        Analyze sentiment of text using FinBERT

        Args:
            text: Text to analyze (post title, body, comments)

        Returns:
            Sentiment score from -1 (bearish) to +1 (bullish), or None if error
        """
        if not self._initialized:
            logger.warning("⚠️ FinBERT not initialized, cannot analyze sentiment")
            return None

        try:
            # Truncate text to max length (512 tokens for BERT)
            if len(text) > 2000:  # Rough character limit
                text = text[:2000]

            # Tokenize input
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # Get model predictions
            with torch.no_grad():
                outputs = self._model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # FinBERT outputs: [negative, neutral, positive]
            negative = predictions[0][0].item()
            neutral = predictions[0][1].item()
            positive = predictions[0][2].item()

            # Convert to sentiment score: -1 (bearish) to +1 (bullish)
            # Weight: positive adds +1, negative adds -1, neutral is 0
            sentiment = positive - negative

            logger.debug(f"FinBERT: pos={positive:.2f}, neu={neutral:.2f}, neg={negative:.2f} → {sentiment:.2f}")

            return sentiment

        except Exception as e:
            logger.error(f"❌ FinBERT analysis error: {e}")
            return None

    def analyze_batch(self, texts: list[str]) -> list[float]:
        """
        Analyze sentiment of multiple texts in batch (more efficient)

        Args:
            texts: List of texts to analyze

        Returns:
            List of sentiment scores
        """
        if not self._initialized:
            logger.warning("⚠️ FinBERT not initialized")
            return [0.0] * len(texts)

        try:
            # Truncate texts
            texts = [t[:2000] if len(t) > 2000 else t for t in texts]

            # Tokenize all texts
            inputs = self._tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # Get predictions for all texts
            with torch.no_grad():
                outputs = self._model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Convert each prediction to sentiment score
            sentiments = []
            for pred in predictions:
                negative = pred[0].item()
                neutral = pred[1].item()
                positive = pred[2].item()
                sentiment = positive - negative
                sentiments.append(sentiment)

            return sentiments

        except Exception as e:
            logger.error(f"❌ FinBERT batch analysis error: {e}")
            return [0.0] * len(texts)


# Global singleton instance
_analyzer = None

def get_finbert_sentiment(text: str) -> Optional[float]:
    """
    Convenience function to get sentiment using FinBERT

    Args:
        text: Text to analyze

    Returns:
        Sentiment score from -1 to +1
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = FinBERTSentimentAnalyzer()
    return _analyzer.analyze(text)


def get_finbert_sentiments_batch(texts: list[str]) -> list[float]:
    """
    Convenience function to get sentiments for multiple texts

    Args:
        texts: List of texts to analyze

    Returns:
        List of sentiment scores
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = FinBERTSentimentAnalyzer()
    return _analyzer.analyze_batch(texts)
