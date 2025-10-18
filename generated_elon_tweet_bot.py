"""
Elon Musk Tesla Sentiment Trading Bot
======================================
This bot monitors Elon Musk's tweets about Tesla and executes trades based on
positive sentiment when TSLA price is below $500.

Exit Strategy: 2% take profit or 1% stop loss

WARNING: This is for educational purposes. Real trading involves significant risk.
"""

import logging
import time
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import re

# Trading
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

# Twitter API (using tweepy)
import tweepy

# Sentiment Analysis
from textblob import TextBlob

# Environment variables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment of tweets using TextBlob"""
    
    @staticmethod
    def analyze(text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with polarity (-1 to 1) and subjectivity (0 to 1)
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    @staticmethod
    def is_positive(text: str, threshold: float = 0.1) -> bool:
        """
        Check if text has positive sentiment
        
        Args:
            text: Text to analyze
            threshold: Minimum polarity to consider positive
            
        Returns:
            True if sentiment is positive
        """
        sentiment = SentimentAnalyzer.analyze(text)
        return sentiment['polarity'] > threshold


class TwitterMonitor:
    """Monitors Twitter for Elon Musk tweets about Tesla"""
    
    def __init__(self, bearer_token: str, target_account: str = "elonmusk"):
        """
        Initialize Twitter monitor
        
        Args:
            bearer_token: Twitter API bearer token
            target_account: Twitter account to monitor (without @)
        """
        self.target_account = target_account
        self.bearer_token = bearer_token
        self.client = None
        self.user_id = None
        self.last_tweet_id = None
        self.keywords = ['Tesla', 'TSLA', 'tesla', 'tsla']
        
        try:
            self.client = tweepy.Client(bearer_token=bearer_token)
            # Get user ID for the target account
            user = self.client.get_user(username=target_account)
            if user.data:
                self.user_id = user.data.id
                logger.info(f"✅ Twitter monitor initialized for @{target_account}")
            else:
                logger.error(f"❌ Could not find user @{target_account}")
        except Exception as e:
            logger.error(f"❌ Error initializing Twitter client: {e}")
    
    def contains_keywords(self, text: str) -> bool:
        """
        Check if text contains Tesla-related keywords
        
        Args:
            text: Text to check
            
        Returns:
            True if keywords found
        """
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    def get_recent_tweets(self, max_results: int = 10) -> List[Dict]:
        """
        Get recent tweets from target account
        
        Args:
            max_results: Maximum number of tweets to retrieve
            
        Returns:
            List of tweet dictionaries
        """
        if not self.client or not self.user_id:
            logger.warning("Twitter client not initialized")
            return []
        
        try:
            tweets = self.client.get_users_tweets(
                id=self.user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'text'],
                since_id=self.last_tweet_id
            )
            
            if tweets.data:
                # Update last tweet ID
                self.last_tweet_id = tweets.data[0].id
                
                return [
                    {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at
                    }
                    for tweet in tweets.data
                ]
            return []
            
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []
    
    def check_for_positive_tesla_tweet(self) -> Optional[Dict]:
        """
        Check for recent positive tweets about Tesla
        
        Returns:
            Tweet dictionary if positive Tesla tweet found, None otherwise
        """
        tweets = self.get_recent_tweets()
        
        for tweet in tweets:
            # Check if tweet contains Tesla keywords
            if self.contains_keywords(tweet['text']):
                logger.info(f"📱 Found Tesla-related tweet: {tweet['text'][:100]}...")
                
                # Check sentiment
                if SentimentAnalyzer.is_positive(tweet['text']):
                    logger.info(f"✅ Positive sentiment detected!")
                    return tweet
                else:
                    logger.info(f"❌ Sentiment not positive enough")
        
        return None


class TradingBot:
    """
    Main trading bot clas