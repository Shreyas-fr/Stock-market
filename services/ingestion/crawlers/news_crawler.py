import httpx
import feedparser
from datetime import datetime
from loguru import logger
from typing import List, Dict, Optional


class NewsCrawler:
    """Fetches news from NewsAPI and RSS feeds."""

    NEWSAPI_BASE = "https://newsapi.org/v2"

    RSS_FEEDS = [
        ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
        ("Bloomberg Markets", "https://feeds.bloomberg.com/markets/news.rss"),
        ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
        ("Financial Express", "https://www.financialexpress.com/feed/"),
        ("Mint Supply Chain", "https://www.livemint.com/rss/economy"),
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def fetch(self, query: str = "supply chain", page_size: int = 20) -> List[Dict]:
        """Fetch news from NewsAPI."""
        articles = []
        
        if self.api_key:
            articles.extend(self._fetch_newsapi(query, page_size))
        
        # Always try RSS feeds
        articles.extend(self._fetch_rss())
        
        return articles

    def _fetch_newsapi(self, query: str, page_size: int) -> List[Dict]:
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(
                    f"{self.NEWSAPI_BASE}/everything",
                    params={
                        "q": query,
                        "pageSize": page_size,
                        "sortBy": "publishedAt",
                        "apiKey": self.api_key,
                        "language": "en",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return [
                        {
                            "headline": a["title"],
                            "body": a.get("content") or a.get("description"),
                            "source_name": a["source"]["name"],
                            "source_url": a["url"],
                            "published_at": a["publishedAt"],
                            "author": a.get("author"),
                        }
                        for a in data.get("articles", [])
                        if a.get("title")
                    ]
        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {e}")
        return []

    def _fetch_rss(self) -> List[Dict]:
        articles = []
        for source_name, feed_url in self.RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    articles.append({
                        "headline": entry.get("title", ""),
                        "body": entry.get("summary", ""),
                        "source_name": source_name,
                        "source_url": entry.get("link", ""),
                        "published_at": entry.get("published", datetime.utcnow().isoformat()),
                    })
            except Exception as e:
                logger.warning(f"RSS fetch failed for {source_name}: {e}")
        return articles

    def save_articles(self, articles: List[Dict]):
        """Save articles to DB (placeholder)."""
        logger.debug(f"Would save {len(articles)} articles")
