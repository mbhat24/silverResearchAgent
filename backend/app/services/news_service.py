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
    "https://www.kitco.com/news/silver/rss",
    "https://www.bullionvault.com/rss/silver-news.xml",
    "https://feeds.feedburner.com/silverdoctors",
    "https://www.investing.com/rss/news_301.rss",  # commodities
]

INDIA_SPECIFIC_FEEDS = [
    "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2141783.cms",
    "https://www.moneycontrol.com/rss/commodities.xml",
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

        # Deduplicate by URL hash
        seen = set()
        unique_items = []
        for item in all_items:
            url_hash = hashlib.md5(item.url.encode()).hexdigest()
            if url_hash not in seen:
                seen.add(url_hash)
                unique_items.append(item)

        # Sort by published date, newest first
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
        """Score how relevant the text is to silver."""
        text_lower = text.lower()
        keywords = ["silver", "xag", "precious metal", "bullion", "white metal",
                     "mcx", "commodity"]
        score = 0.0
        for kw in keywords:
            if kw in text_lower:
                score += 0.15
        return min(score, 1.0)

    async def search_news(self, query: str) -> list[NewsItem]:
        """Search for specific silver-related news."""
        all_news = await self.fetch_news(limit=50)
        query_lower = query.lower()
        return [
            item for item in all_news
            if query_lower in item.title.lower() or query_lower in item.summary.lower()
        ]
