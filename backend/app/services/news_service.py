import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import httpx
import feedparser
from bs4 import BeautifulSoup

from ..models.schemas import NewsItem
from ..config import get_settings

settings = get_settings()

# RSS feeds for silver/precious metals news
SILVER_RSS_FEEDS = [
    "https://news.google.com/rss/search?q=silver+price+precious+metals&hl=en-US&gl=US&ceid=US:en",
    "https://www.metalsdaily.com/news/silver-news/feed/",
    "https://www.kitco.com/news/silver/rss",
    "https://silverseek.com/rss.xml",
    "https://goldsilver.com/feed/",
]

INDIA_SPECIFIC_FEEDS = [
    "https://news.google.com/rss/search?q=silver+price+India+MCX&hl=en-IN&gl=IN&ceid=IN:en",
    "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2141783.cms",
]


class NewsService:
    """Aggregates silver-related news from multiple sources."""

    async def fetch_news(self, limit: int = 20) -> list[NewsItem]:
        """Fetch latest silver news from all sources."""
        all_items = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            tasks = []
            for feed_url in SILVER_RSS_FEEDS + INDIA_SPECIFIC_FEEDS:
                tasks.append(self._parse_feed(client, feed_url))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_items.extend(result)

        # Filter out non-silver articles (require relevance_score > 0)
        silver_items = [item for item in all_items if item.relevance_score > 0]

        if not silver_items:
            return []

        # Deduplicate by URL hash
        seen = set()
        unique_items = []
        for item in silver_items:
            url_hash = hashlib.md5(item.url.encode()).hexdigest()
            if url_hash not in seen:
                seen.add(url_hash)
                unique_items.append(item)

        # Sort by relevance (highest first), then by published date (newest first)
        unique_items.sort(key=lambda x: (-x.relevance_score, x.published_at), reverse=True)
        unique_items.sort(key=lambda x: x.published_at, reverse=True)
        return unique_items[:limit]

    async def _parse_feed(self, client: httpx.AsyncClient, url: str) -> list[NewsItem]:
        """Parse an RSS feed and extract news items."""
        try:
            response = await client.get(url)
            feed = feedparser.parse(response.text)

            items = []
            for entry in feed.entries[:10]:
                published = datetime.now()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])

                # Clean summary
                summary = ""
                if hasattr(entry, "summary"):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary = soup.get_text()[:300]
                elif hasattr(entry, "description"):
                    soup = BeautifulSoup(entry.description, "html.parser")
                    summary = soup.get_text()[:300]

                items.append(NewsItem(
                    title=entry.title if hasattr(entry, "title") else "Untitled",
                    source=feed.feed.title if hasattr(feed.feed, "title") else url,
                    url=entry.link if hasattr(entry, "link") else "",
                    published_at=published,
                    summary=summary,
                    relevance_score=self._calculate_relevance(entry.title + " " + summary)
                ))

            return items
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")
            return []

    def _calculate_relevance(self, text: str) -> float:
        """Score how relevant the text is to silver. Returns 0 for non-silver content."""
        text_lower = text.lower()
        primary_keywords = ["silver", "xag", "precious metal", "bullion", "white metal"]
        secondary_keywords = ["mcx", "commodity", "gold", "metal", "mine", "mining",
                              "etf", "futures", "spot price", "troy ounce"]
        score = 0.0
        for kw in primary_keywords:
            if kw in text_lower:
                score += 0.25
        for kw in secondary_keywords:
            if kw in text_lower:
                score += 0.1
        return min(score, 1.0)

    async def search_news(self, query: str) -> list[NewsItem]:
        """Search for specific silver-related news."""
        all_news = await self.fetch_news(limit=50)
        query_lower = query.lower()
        return [
            item for item in all_news
            if query_lower in item.title.lower() or query_lower in item.summary.lower()
        ]
