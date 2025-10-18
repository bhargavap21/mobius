"""
Web Scraping Tools - Extract data from any website

Supports both static and JavaScript-rendered pages
"""

import logging
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


def scrape_website(
    url: str,
    selector: Optional[str] = None,
    extract_type: str = "text",
    javascript: bool = False,
) -> Dict[str, Any]:
    """
    Scrape data from a website

    Args:
        url: Website URL to scrape
        selector: CSS selector to target specific elements (optional)
        extract_type: What to extract - "text", "links", "table"
        javascript: Whether to render JavaScript (uses Playwright)

    Returns:
        Scraped data
    """
    try:
        logger.info(f"🌐 Scraping: {url}")
        logger.info(f"   Selector: {selector or 'entire page'}")
        logger.info(f"   Extract: {extract_type}")
        logger.info(f"   JavaScript: {javascript}")

        if javascript:
            return _scrape_with_javascript(url, selector, extract_type)
        else:
            return _scrape_static(url, selector, extract_type)

    except Exception as e:
        logger.error(f"❌ Error scraping {url}: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
        }


def _scrape_static(
    url: str,
    selector: Optional[str],
    extract_type: str,
) -> Dict[str, Any]:
    """
    Scrape static HTML pages (no JavaScript)

    Args:
        url: URL to scrape
        selector: CSS selector
        extract_type: What to extract

    Returns:
        Scraped data
    """
    # Add headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")

    # Extract based on type
    if extract_type == "text":
        result = _extract_text(soup, selector)
    elif extract_type == "links":
        result = _extract_links(soup, selector, url)
    elif extract_type == "table":
        result = _extract_tables(soup, selector)
    else:
        result = {"text": soup.get_text(separator=" ", strip=True)[:1000]}

    logger.info(f"✅ Successfully scraped {url}")

    return {
        "success": True,
        "url": url,
        "selector": selector,
        "extract_type": extract_type,
        "data": result,
    }


def _scrape_with_javascript(
    url: str,
    selector: Optional[str],
    extract_type: str,
) -> Dict[str, Any]:
    """
    Scrape pages that require JavaScript rendering

    Args:
        url: URL to scrape
        selector: CSS selector
        extract_type: What to extract

    Returns:
        Scraped data
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate and wait for content
            page.goto(url, wait_until="networkidle")

            # Get rendered HTML
            content = page.content()
            browser.close()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, "lxml")

        # Extract based on type
        if extract_type == "text":
            result = _extract_text(soup, selector)
        elif extract_type == "links":
            result = _extract_links(soup, selector, url)
        elif extract_type == "table":
            result = _extract_tables(soup, selector)
        else:
            result = {"text": soup.get_text(separator=" ", strip=True)[:1000]}

        logger.info(f"✅ Successfully scraped {url} with JavaScript")

        return {
            "success": True,
            "url": url,
            "selector": selector,
            "extract_type": extract_type,
            "javascript": True,
            "data": result,
        }

    except ImportError:
        logger.error("❌ Playwright not installed for JavaScript rendering")
        return {
            "success": False,
            "error": "Playwright not installed. Run: playwright install chromium",
            "url": url,
        }
    except Exception as e:
        logger.error(f"❌ Error scraping with JavaScript: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
        }


def _extract_text(soup: BeautifulSoup, selector: Optional[str]) -> Dict[str, Any]:
    """Extract text content"""
    if selector:
        elements = soup.select(selector)
        texts = [el.get_text(strip=True) for el in elements]
        return {
            "count": len(texts),
            "texts": texts[:20],  # Limit to 20 items
        }
    else:
        return {
            "text": soup.get_text(separator=" ", strip=True)[:2000],  # First 2000 chars
        }


def _extract_links(
    soup: BeautifulSoup, selector: Optional[str], base_url: str
) -> Dict[str, Any]:
    """Extract links"""
    if selector:
        elements = soup.select(selector)
        links = []
        for el in elements:
            href = el.get("href")
            if href:
                # Make absolute URLs
                absolute_url = urljoin(base_url, href)
                links.append(
                    {
                        "text": el.get_text(strip=True),
                        "url": absolute_url,
                    }
                )
    else:
        links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            absolute_url = urljoin(base_url, href)
            links.append(
                {
                    "text": a.get_text(strip=True),
                    "url": absolute_url,
                }
            )

    return {
        "count": len(links),
        "links": links[:20],  # Limit to 20
    }


def _extract_tables(soup: BeautifulSoup, selector: Optional[str]) -> Dict[str, Any]:
    """Extract table data"""
    if selector:
        tables = soup.select(selector)
    else:
        tables = soup.find_all("table")

    extracted_tables = []

    for table in tables[:5]:  # Limit to 5 tables
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)

        if rows:
            extracted_tables.append(
                {
                    "headers": rows[0] if rows else [],
                    "rows": rows[1:10] if len(rows) > 1 else [],  # Max 10 rows
                    "total_rows": len(rows),
                }
            )

    return {
        "count": len(extracted_tables),
        "tables": extracted_tables,
    }


def scrape_company_news(company_name: str, ticker: str) -> Dict[str, Any]:
    """
    Scrape recent news about a company

    Args:
        company_name: Company name (e.g., "Tesla")
        ticker: Stock ticker (e.g., "TSLA")

    Returns:
        Recent news articles
    """
    try:
        logger.info(f"📰 Scraping news for {company_name} ({ticker})")

        # For hackathon, we'll return mock news
        # In production, you'd use NewsAPI or scrape Google News
        logger.warning("⚠️  Using mock news data (NewsAPI not implemented)")

        return _mock_company_news(company_name, ticker)

    except Exception as e:
        logger.error(f"❌ Error scraping news for {company_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "company": company_name,
        }


def _mock_company_news(company_name: str, ticker: str) -> Dict[str, Any]:
    """Generate mock news data"""
    mock_news = {
        "TSLA": [
            {
                "title": "Tesla Announces Record Q4 Deliveries",
                "source": "Reuters",
                "published": "2 hours ago",
                "sentiment": "positive",
                "summary": "Tesla delivered record numbers in Q4, exceeding analyst expectations.",
            },
            {
                "title": "Cybertruck Production Ramps Up",
                "source": "Bloomberg",
                "published": "5 hours ago",
                "sentiment": "positive",
                "summary": "Tesla increases Cybertruck production capacity at Giga Texas.",
            },
            {
                "title": "Analysts Debate Tesla's Valuation",
                "source": "CNBC",
                "published": "1 day ago",
                "sentiment": "neutral",
                "summary": "Wall Street analysts split on Tesla's current stock price.",
            },
        ],
        "AAPL": [
            {
                "title": "Apple Vision Pro Sales Exceed Expectations",
                "source": "TechCrunch",
                "published": "3 hours ago",
                "sentiment": "positive",
                "summary": "Vision Pro sees strong early adoption among developers.",
            },
        ],
        "NVDA": [
            {
                "title": "NVIDIA Unveils Next-Gen AI Chips",
                "source": "The Verge",
                "published": "1 hour ago",
                "sentiment": "very_positive",
                "summary": "New Blackwell GPU architecture promises 2x performance.",
            },
        ],
    }

    articles = mock_news.get(
        ticker.upper(),
        [
            {
                "title": f"{company_name} Stock Analysis Update",
                "source": "Financial Times",
                "published": "6 hours ago",
                "sentiment": "neutral",
                "summary": f"Market analysts provide update on {company_name} stock.",
            }
        ],
    )

    return {
        "success": True,
        "company": company_name,
        "ticker": ticker,
        "articles_count": len(articles),
        "articles": articles,
        "note": "⚠️  Using mock news data (NewsAPI not configured)",
    }


def monitor_company_website(ticker: str, company_url: str) -> Dict[str, Any]:
    """
    Monitor a company's investor relations or press release page

    Args:
        ticker: Stock ticker
        company_url: URL to monitor (e.g., investor relations page)

    Returns:
        Recent updates from company website
    """
    try:
        logger.info(f"🏢 Monitoring {ticker} website: {company_url}")

        # Scrape the page
        result = scrape_website(company_url, extract_type="links")

        if not result["success"]:
            return result

        # Filter for recent press releases or announcements
        links = result["data"].get("links", [])
        recent_updates = []

        keywords = ["press", "release", "announcement", "news", "investor"]

        for link in links:
            text = link["text"].lower()
            if any(keyword in text for keyword in keywords):
                recent_updates.append(link)

        return {
            "success": True,
            "ticker": ticker,
            "url": company_url,
            "updates_count": len(recent_updates),
            "recent_updates": recent_updates[:10],
            "last_checked": "now",
        }

    except Exception as e:
        logger.error(f"❌ Error monitoring {ticker} website: {e}")
        return {
            "success": False,
            "error": str(e),
            "ticker": ticker,
        }


# Tool schemas for Claude
WEB_SCRAPING_TOOLS = [
    {
        "name": "scrape_website",
        "description": "Extract data from any website. Can get text content, links, or tables. Use this to gather information from company websites, news sites, or any public webpage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Website URL to scrape (must be full URL including https://)",
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector to target specific elements (optional). Example: '.article-title', '#main-content'",
                },
                "extract_type": {
                    "type": "string",
                    "enum": ["text", "links", "table"],
                    "description": "What to extract from the page",
                    "default": "text",
                },
                "javascript": {
                    "type": "boolean",
                    "description": "Whether page requires JavaScript rendering (default: false)",
                    "default": False,
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "scrape_company_news",
        "description": "Get recent news articles about a company. Returns headlines, summaries, and sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Company name (e.g., 'Tesla', 'Apple')",
                },
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'TSLA', 'AAPL')",
                },
            },
            "required": ["company_name", "ticker"],
        },
    },
]
