"""
Web scraping module using Crawl4AI.

Extracts clean text content from web pages, bypassing bot detection.
"""

import asyncio
from typing import Optional
from crawl4ai import AsyncWebCrawler


class WebScraper:
    """Web scraper using Crawl4AI with browser automation."""

    def __init__(self):
        self.crawler = None

    async def scrape_url(self, url: str, timeout: int = 15) -> Optional[str]:
        """
        Scrape clean text content from a URL.

        Args:
            url: The URL to scrape
            timeout: Timeout in seconds for the scraping operation

        Returns:
            Cleaned text content, or None if scraping failed
        """
        try:
            # Create a new crawler instance for this scrape
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await asyncio.wait_for(
                    crawler.arun(url=url),
                    timeout=timeout
                )

                if result.success and result.markdown:
                    # Return the markdown content which is cleaner than raw HTML
                    return result.markdown

                return None

        except asyncio.TimeoutError:
            print(f"Timeout scraping {url}")
            return None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

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
