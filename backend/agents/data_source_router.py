"""
Data Source Router Agent
Analyzes user queries and intelligently routes to optimal data extraction method
"""

import logging
import json
import re
from typing import Dict, List, Any
from anthropic import Anthropic

from tools.extraction.data_source_registry import get_registry
from config import settings

logger = logging.getLogger(__name__)


class DataSourceRouterAgent:
    """
    Intelligent routing agent for data extraction

    This agent:
    1. Analyzes user's trading strategy description
    2. Identifies what data sources are needed
    3. Determines optimal extraction method for each source
    4. Generates complete extraction plan with schedule

    Example:
        Query: "Trade Tesla on Elon's tweets"
        Output: {
            "sources": [{
                "name": "twitter_elonmusk",
                "method": "apify",
                "actor": "apify/twitter-scraper",
                "config": {"username": "elonmusk", "keywords": ["Tesla", "TSLA"]}
            }]
        }
    """

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.registry = get_registry()
        logger.info("🧠 DataSourceRouterAgent initialized")

    async def plan_extraction(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive extraction plan from user query

        Args:
            request: {
                "user_query": "Trade Tesla on Elon's tweets and WSB sentiment",
                "strategy": {...parsed strategy (optional)...}
            }

        Returns:
            {
                "sources": [{...source configs...}],
                "schedule": "realtime" | "5min" | "1hour",
                "confidence": 0.0-1.0,
                "estimated_cost": {...}
            }
        """
        user_query = request.get("user_query", "")

        logger.info(f"📊 Analyzing query for data requirements: '{user_query[:100]}...'")

        # Step 1: Use Claude to extract data requirements
        data_requirements = await self._extract_data_requirements(user_query)

        if not data_requirements:
            logger.warning("⚠️  No data sources identified in query")
            return {
                "sources": [],
                "schedule": "daily",
                "confidence": 0.0,
                "estimated_cost": {"estimated_monthly_cost": 0}
            }

        # Step 2: Route each requirement to optimal method
        sources = []
        for req in data_requirements:
            source_config = await self._route_source(req)
            if source_config:
                sources.append(source_config)

        # Step 3: Determine optimal schedule
        schedule = self._determine_schedule(data_requirements)

        # Step 4: Estimate costs
        cost_estimate = self._estimate_cost(sources, schedule)

        result = {
            "sources": sources,
            "schedule": schedule,
            "confidence": self._calculate_confidence(sources),
            "estimated_cost": cost_estimate
        }

        logger.info(f"✅ Generated extraction plan: {len(sources)} sources, {schedule} schedule")
        return result

    async def _extract_data_requirements(self, user_query: str) -> List[Dict]:
        """
        Use Claude to understand what data the user wants

        Returns:
            [
              {
                "source": "twitter.com",
                "target": "elonmusk",
                "data_type": "tweets",
                "filters": {"keywords": ["Tesla", "TSLA"]},
                "frequency": "realtime"
              },
              ...
            ]
        """
        prompt = f"""Analyze this trading strategy request and extract ALL data source requirements:

User Query: "{user_query}"

Identify:
1. **All data sources mentioned** (websites, platforms, social media accounts)
2. **Type of data needed** (sentiment, posts, articles, tweets, trades, prices)
3. **Specific targets** (username, subreddit, ticker, hashtag, keyword)
4. **Filters** (keywords, date ranges, engagement thresholds)
5. **Update frequency** (realtime, hourly, daily)

Return ONLY a JSON array (no markdown, no explanation):
[
  {{
    "source": "twitter.com" | "reddit.com" | "news" | etc,
    "target": "username" | "subreddit" | "ticker",
    "data_type": "tweets" | "posts" | "articles" | "sentiment",
    "filters": {{"keywords": ["TSLA"], "min_engagement": 100}},
    "frequency": "realtime" | "5min" | "1hour" | "daily"
  }}
]

Examples:
- "Trade Tesla on Elon's tweets" → [{{"source": "twitter.com", "target": "elonmusk", "data_type": "tweets", "filters": {{"keywords": ["Tesla", "TSLA"]}}, "frequency": "realtime"}}]
- "Trade on r/wallstreetbets sentiment" → [{{"source": "reddit.com", "target": "wallstreetbets", "data_type": "posts", "filters": {{}}, "frequency": "1hour"}}]
- "Trade on WSB + Elon tweets" → [{{reddit}}, {{twitter}}]

If NO data sources mentioned, return []
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text.strip()

            # Extract JSON from response
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                requirements = json.loads(json_match.group(0))
                logger.info(f"📋 Extracted {len(requirements)} data requirements")
                return requirements
            else:
                logger.warning("⚠️  No valid JSON in Claude response")
                return []

        except Exception as e:
            logger.error(f"❌ Error extracting data requirements: {e}")
            return []

    async def _route_source(self, requirement: Dict) -> Dict:
        """
        Determine optimal extraction method for a data requirement

        Priority:
        1. Check if official API exists → use API
        2. Check if Apify actor exists → use Apify
        3. Check if Firecrawl can handle (static site) → use Firecrawl
        4. Generate Browserbase scraper → use Browserbase
        """
        source = requirement.get("source", "")
        target = requirement.get("target", "")
        data_type = requirement.get("data_type", "")
        filters = requirement.get("filters", {})
        frequency = requirement.get("frequency", "1hour")

        # Normalize source name
        source = source.lower().strip()

        # Check registry for known source
        known_source = self.registry.lookup(source)

        if known_source and known_source["method"] == "api":
            logger.info(f"✅ Routing '{source}' → API (official API available)")
            return {
                "name": f"{source.replace('.com', '')}_{target or 'default'}",
                "source": source,
                "method": "api",
                "handler": known_source["handler"],
                "config": {
                    "target": target,
                    "data_type": data_type,
                    "filters": filters,
                    "frequency": frequency
                },
                "cost_per_call": 0  # Most APIs are free
            }

        elif known_source and known_source["method"] == "apify":
            logger.info(f"✅ Routing '{source}' → Apify (actor available)")
            return {
                "name": f"{source.replace('.com', '')}_{target or 'default'}",
                "source": source,
                "method": "apify",
                "actor": known_source["actor"],
                "config": {
                    "username": target,
                    "keywords": filters.get("keywords", []),
                    "frequency": frequency,
                    **filters
                },
                "cost_per_call": 0.005  # ~$5/1000 calls
            }

        elif self._is_static_site(source):
            logger.info(f"✅ Routing '{source}' → Firecrawl (static content)")
            return {
                "name": f"{source.replace('.com', '')}_{target or 'content'}",
                "source": source,
                "method": "firecrawl",
                "config": {
                    "url": f"https://{source}",
                    "selectors": filters.get("selectors"),
                    "frequency": frequency
                },
                "cost_per_call": 0.0005  # ~$0.50/1000 pages
            }

        else:
            # Need custom scraper (Browserbase)
            logger.info(f"⚠️  Routing '{source}' → Browserbase (custom scraper needed)")
            return {
                "name": f"{source.replace('.com', '')}_{target or 'custom'}",
                "source": source,
                "method": "browserbase",
                "needs_generation": True,
                "config": {
                    "url": f"https://{source}",
                    "data_requirements": requirement,
                    "frequency": frequency
                },
                "cost_per_call": 0.01  # ~$10/1000 page loads
            }

    def _determine_schedule(self, requirements: List[Dict]) -> str:
        """
        Determine optimal extraction schedule based on all requirements
        """
        frequencies = [req.get("frequency", "1hour") for req in requirements]

        # Frequency priority (most frequent wins)
        freq_priority = {
            "realtime": 1,
            "5min": 2,
            "15min": 3,
            "1hour": 4,
            "6hour": 5,
            "daily": 6
        }

        # Get most frequent requirement
        best_freq = min(frequencies, key=lambda f: freq_priority.get(f, 999))
        return best_freq

    def _calculate_confidence(self, sources: List[Dict]) -> float:
        """
        Calculate confidence in extraction plan

        High confidence if using known methods (API/Apify)
        Lower confidence if needing custom scrapers
        """
        if not sources:
            return 0.0

        # Score by method reliability
        method_scores = {
            "api": 1.0,      # Official APIs are most reliable
            "apify": 0.9,    # Apify is proven but paid
            "firecrawl": 0.7,  # Static scraping is simpler
            "browserbase": 0.5  # Custom scrapers need testing
        }

        total_score = sum(method_scores.get(s.get("method"), 0.3) for s in sources)
        return min(1.0, total_score / len(sources))

    def _estimate_cost(self, sources: List[Dict], schedule: str) -> Dict:
        """
        Estimate monthly cost for extraction plan
        """
        # Calls per month by schedule
        schedule_multiplier = {
            "realtime": 43200,  # Every minute
            "5min": 8640,
            "15min": 2880,
            "1hour": 720,
            "6hour": 120,
            "daily": 30
        }

        calls_per_month = schedule_multiplier.get(schedule, 720)

        total_cost = 0
        breakdown = []

        for source in sources:
            cost_per_call = source.get("cost_per_call", 0.001)
            source_cost = calls_per_month * cost_per_call

            breakdown.append({
                "source": source.get("name"),
                "method": source.get("method"),
                "calls_per_month": calls_per_month,
                "cost": round(source_cost, 2)
            })

            total_cost += source_cost

        return {
            "estimated_monthly_cost": round(total_cost, 2),
            "calls_per_month": calls_per_month,
            "breakdown": breakdown
        }

    def _is_static_site(self, source: str) -> bool:
        """
        Heuristic to detect if site is static (good for Firecrawl)
        """
        static_indicators = [
            "blog", "medium.com", ".wordpress.com", "substack.com",
            "news", "article", "post", "docs"
        ]
        return any(ind in source.lower() for ind in static_indicators)
