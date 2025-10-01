"""
Simple keyword-based search for content retrieval.

This module implements a basic keyword matching system for finding
relevant content chunks to answer questions. In the future, this will
be replaced with vector embeddings (ChromaDB) for semantic search.
"""

import re
from typing import List, Tuple


class SimpleSearch:
    """Keyword-based search engine for content retrieval."""

    def __init__(self):
        pass

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text.

        Args:
            text: Input text to extract keywords from

        Returns:
            List of keywords
        """
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation and split into words
        words = re.findall(r'\b[a-z]{3,}\b', text)

        # Filter out common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get',
            'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old',
            'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let',
            'put', 'say', 'she', 'too', 'use', 'what', 'when', 'where',
            'with', 'that', 'this', 'have', 'from', 'they', 'been',
            'about', 'there', 'which', 'their', 'would', 'these',
            'than', 'your'
        }

        keywords = [w for w in words if w not in stop_words]

        return keywords

    def _score_chunk(self, chunk: str, keywords: List[str]) -> float:
        """
        Score a content chunk based on keyword matches.

        Args:
            chunk: Content chunk to score
            keywords: List of keywords to match

        Returns:
            Score (higher is better)
        """
        chunk_lower = chunk.lower()
        score = 0.0

        for keyword in keywords:
            # Count occurrences of each keyword
            count = chunk_lower.count(keyword)
            # Higher weight for more occurrences
            score += count * 1.0

        return score

    def search(
        self,
        question: str,
        content_chunks: List[str],
        top_k: int = 3,
        max_chars: int = 4000
    ) -> List[str]:
        """
        Search for relevant content chunks based on a question.

        Args:
            question: The question to answer
            content_chunks: List of content chunks to search
            top_k: Number of top chunks to return
            max_chars: Maximum total characters to return

        Returns:
            List of relevant content chunks
        """
        if not content_chunks:
            return []

        # Extract keywords from the question
        keywords = self._extract_keywords(question)

        if not keywords:
            # If no keywords, return first few chunks
            return content_chunks[:top_k]

        # Score each chunk
        scored_chunks: List[Tuple[float, str]] = []

        for chunk in content_chunks:
            score = self._score_chunk(chunk, keywords)
            scored_chunks.append((score, chunk))

        # Sort by score (highest first)
        scored_chunks.sort(reverse=True, key=lambda x: x[0])

        # Take top_k chunks
        top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]

        # Limit total characters
        total_chars = 0
        limited_chunks = []

        for chunk in top_chunks:
            if total_chars + len(chunk) <= max_chars:
                limited_chunks.append(chunk)
                total_chars += len(chunk)
            else:
                # Add partial chunk if it fits
                remaining = max_chars - total_chars
                if remaining > 500:  # Only add if we can get a meaningful portion
                    limited_chunks.append(chunk[:remaining])
                break

        return limited_chunks
