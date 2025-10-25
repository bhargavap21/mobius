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

        # News API requires implementation
        logger.error("❌ News scraping not implemented - requires NewsAPI or web scraping integration")

        return {
            "success": False,
            "error": "News scraping requires API integration. Please implement data extraction pipeline.",
            "company": company_name,
            "ticker": ticker,
        }

    except Exception as e:
        logger.error(f"❌ Error scraping news for {company_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "company": company_name,
        }


# Tool schemas for Claude
WEB_SCRAPING_TOOLS = [
    {
        "name": "scrape_website",
        "description": "Scrape content from a website URL. Extract text, links, and tables.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL to scrape (e.g., 'https://example.com')",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "scrape_company_news",
        "description": "Scrape recent news articles about a company (requires NewsAPI or implementation).",
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
