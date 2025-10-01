"""
Web scraping module with fallback options.

Tries Crawl4AI first, falls back to simple HTTP scraping if browser automation fails.
"""

import asyncio
from typing import Optional
import httpx
from bs4 import BeautifulSoup

try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("[Scraper] Crawl4AI not available, using fallback scraper")


class WebScraper:
    """Web scraper with Crawl4AI and HTTP fallback."""

    def __init__(self):
        self.crawler = None

    async def _scrape_with_crawl4ai(self, url: str, timeout: int) -> Optional[str]:
        """Try scraping with Crawl4AI browser automation."""
        if not CRAWL4AI_AVAILABLE:
            return None

        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await asyncio.wait_for(
                    crawler.arun(url=url),
                    timeout=timeout
                )

                if result.success and result.markdown:
                    print(f"[Scraper] Crawl4AI success for {url}")
                    return result.markdown

                return None

        except Exception as e:
            print(f"[Scraper] Crawl4AI failed for {url}: {type(e).__name__}: {e}")
            return None

    async def _scrape_with_http(self, url: str, timeout: int) -> Optional[str]:
        """Fallback: Simple HTTP scraping with BeautifulSoup."""
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    url,
                    timeout=timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    # Get text
                    text = soup.get_text(separator='\n', strip=True)

                    # Clean up whitespace
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    cleaned_text = '\n'.join(lines)

                    print(f"[Scraper] HTTP fallback success for {url} ({len(cleaned_text)} chars)")
                    return cleaned_text

                print(f"[Scraper] HTTP fallback failed for {url}: status {response.status_code}")
                return None

        except Exception as e:
            print(f"[Scraper] HTTP fallback error for {url}: {type(e).__name__}: {e}")
            return None

    async def scrape_url(self, url: str, timeout: int = 15) -> Optional[str]:
        """
        Scrape clean text content from a URL.
        Tries Crawl4AI first, falls back to simple HTTP scraping.

        Args:
            url: The URL to scrape
            timeout: Timeout in seconds for the scraping operation

        Returns:
            Cleaned text content, or None if scraping failed
        """
        # Try Crawl4AI first
        result = await self._scrape_with_crawl4ai(url, timeout)
        if result:
            return result

        # Fallback to simple HTTP scraping
        print(f"[Scraper] Falling back to HTTP scraping for {url}")
        return await self._scrape_with_http(url, timeout)

    async def scrape_multiple(self, urls: list[str], timeout: int = 15) -> dict[str, Optional[str]]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            timeout: Timeout in seconds per URL

        Returns:
            Dictionary mapping URLs to their scraped content
        """
        tasks = [self.scrape_url(url, timeout) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scraped_data = {}
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                print(f"Exception scraping {url}: {result}")
                scraped_data[url] = None
            else:
                scraped_data[url] = result

        return scraped_data
