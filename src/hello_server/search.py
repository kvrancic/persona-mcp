"""
Web search module using Serper API.

Finds relevant content about a person using targeted search queries.
"""

import httpx
from typing import List, Dict


class SerperSearch:
    """Interface to Serper API for web search."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"

    async def search_person(self, person_name: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Search for content about a person.

        Args:
            person_name: Name of the person to search for
            max_results: Maximum number of results to return

        Returns:
            List of dictionaries with 'url', 'title', and 'snippet' keys
        """
        # Create targeted search queries
        queries = [
            f'"{person_name}" interview',
            f'"{person_name}" quotes',
            f'"{person_name}" blog',
            f'"{person_name}" opinions',
        ]

        all_results = []

        async with httpx.AsyncClient() as client:
            for query in queries:
                try:
                    response = await client.post(
                        self.base_url,
                        headers={
                            "X-API-KEY": self.api_key,
                            "Content-Type": "application/json"
                        },
                        json={
                            "q": query,
                            "num": max_results // len(queries) + 1  # Distribute across queries
                        },
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        organic_results = data.get("organic", [])

                        for result in organic_results:
                            all_results.append({
                                "url": result.get("link", ""),
                                "title": result.get("title", ""),
                                "snippet": result.get("snippet", "")
                            })

                except Exception as e:
                    print(f"Search error for query '{query}': {e}")
                    continue

        # Deduplicate by URL and limit to max_results
        seen_urls = set()
        unique_results = []

        for result in all_results:
            url = result["url"]
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

            if len(unique_results) >= max_results:
                break

        return unique_results[:max_results]
