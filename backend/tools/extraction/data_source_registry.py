"""
Data Source Registry
Central registry of known data sources and optimal extraction methods
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataSourceRegistry:
    """
    Registry of known data sources and their optimal extraction methods

    This acts as a knowledge base that maps data sources to:
    - Best extraction method (API, Apify, Browserbase, Firecrawl)
    - Configuration details
    - Cost estimates
    - Rate limits
    """

    # Known data sources and their optimal extraction methods
    KNOWN_SOURCES = {
        # Social Media - APIs (Tier 1)
        "reddit.com": {
            "method": "api",
            "handler": "reddit_handler",
            "api_name": "PRAW",
            "cost": "free",
            "rate_limit": "60/min",
            "requires_auth": True,
            "description": "Reddit posts and comments via official API"
        },

        "youtube.com": {
            "method": "api",
            "handler": "youtube_handler",
            "api_name": "YouTube Data API",
            "cost": "free",
            "rate_limit": "10000/day",
            "requires_auth": True,
            "description": "YouTube videos, comments, and metadata"
        },

        # Social Media - Apify (Tier 2)
        "twitter.com": {
            "method": "apify",
            "actor": "apify/twitter-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "Twitter/X posts via Apify scraper"
        },

        "x.com": {
            "method": "apify",
            "actor": "apify/twitter-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "Twitter/X posts via Apify scraper (new domain)"
        },

        "instagram.com": {
            "method": "apify",
            "actor": "apify/instagram-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "Instagram posts and profiles"
        },

        "tiktok.com": {
            "method": "apify",
            "actor": "apify/tiktok-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "TikTok videos and trends"
        },

        "linkedin.com": {
            "method": "apify",
            "actor": "apify/linkedin-scraper",
            "cost": "$5/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "LinkedIn posts and profiles"
        },

        # News APIs (Tier 1)
        "newsapi.org": {
            "method": "api",
            "handler": "news_handler",
            "api_name": "NewsAPI",
            "cost": "free",
            "rate_limit": "100/day (free tier)",
            "requires_auth": True,
            "description": "News articles from 80,000+ sources"
        },

        # Financial Data APIs (Tier 1)
        "sec.gov": {
            "method": "api",
            "handler": "sec_handler",
            "api_name": "SEC Edgar",
            "cost": "free",
            "rate_limit": "10/sec",
            "requires_auth": False,
            "description": "SEC filings and company data"
        },

        # Static Content - Firecrawl (Tier 4)
        "medium.com": {
            "method": "firecrawl",
            "cost": "$0.50/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "Medium articles and posts"
        },

        "substack.com": {
            "method": "firecrawl",
            "cost": "$0.50/1000",
            "rate_limit": "unlimited",
            "requires_auth": False,
            "description": "Substack newsletters"
        },
    }

    def __init__(self):
        logger.info(f"📚 DataSourceRegistry initialized with {len(self.KNOWN_SOURCES)} known sources")

    def lookup(self, source: str) -> Optional[Dict]:
        """
        Look up the best extraction method for a data source

        Args:
            source: Domain or platform name (e.g., "reddit.com", "twitter", "reddit")

        Returns:
            Configuration dict or None if not found
        """
        # Normalize source
        source = source.lower().strip()

        # Exact match
        if source in self.KNOWN_SOURCES:
            logger.info(f"✅ Found exact match for '{source}' → {self.KNOWN_SOURCES[source]['method']}")
            return self.KNOWN_SOURCES[source]

        # Partial match (e.g., "reddit" matches "reddit.com")
        for known_source, config in self.KNOWN_SOURCES.items():
            if source in known_source or known_source.split('.')[0] in source:
                logger.info(f"✅ Found partial match '{source}' → '{known_source}' → {config['method']}")
                return config

        # Not found
        logger.warning(f"⚠️  No known configuration for '{source}' → will require custom scraper")
        return None

    def get_by_method(self, method: str) -> Dict[str, Dict]:
        """
        Get all sources that use a specific extraction method

        Args:
            method: "api", "apify", "browserbase", or "firecrawl"

        Returns:
            Dict of sources using that method
        """
        return {
            source: config
            for source, config in self.KNOWN_SOURCES.items()
            if config["method"] == method
        }

    def get_all_sources(self) -> Dict[str, Dict]:
        """Get all known sources"""
        return self.KNOWN_SOURCES.copy()

    def get_stats(self) -> Dict:
        """Get registry statistics"""
        stats = {
            "total_sources": len(self.KNOWN_SOURCES),
            "by_method": {},
            "free_sources": 0,
            "paid_sources": 0,
        }

        for config in self.KNOWN_SOURCES.values():
            method = config["method"]
            stats["by_method"][method] = stats["by_method"].get(method, 0) + 1

            if config["cost"] == "free":
                stats["free_sources"] += 1
            else:
                stats["paid_sources"] += 1

        return stats


# Singleton instance
_registry = None

def get_registry() -> DataSourceRegistry:
    """Get the global registry instance"""
    global _registry
    if _registry is None:
        _registry = DataSourceRegistry()
    return _registry
