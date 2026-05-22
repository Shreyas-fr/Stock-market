import feedparser
import httpx
from datetime import datetime
from loguru import logger
from typing import List, Dict, Optional


class PolicyCrawler:
    """Crawls government sources for policy announcements."""

    SOURCES = [
        {
            "name": "PIB India",
            "country": "IND",
            "url": "https://pib.gov.in/RSSNewsCategoryWise.aspx?Category=1",
            "type": "rss",
        },
        {
            "name": "White House",
            "country": "USA",
            "url": "https://www.whitehouse.gov/feed/",
            "type": "rss",
        },
        {
            "name": "SEC EDGAR",
            "country": "USA",
            "url": "https://efts.sec.gov/LATEST/search-index?q=%22supply+chain%22&dateRange=custom&startdt={start_date}&enddt={end_date}&forms=8-K",
            "type": "api",
        },
        {
            "name": "RBI Notifications",
            "country": "IND",
            "url": "https://rbi.org.in/Scripts/RSS.aspx",
            "type": "rss",
        },
        {
            "name": "WTO News",
            "country": "INTL",
            "url": "https://www.wto.org/english/news_e/rss_e/rss_e.htm",
            "type": "rss",
        },
    ]

    def fetch_all(self) -> List[Dict]:
        """Fetch from all policy sources."""
        all_policies = []
        for source in self.SOURCES:
            try:
                if source["type"] == "rss":
                    policies = self._fetch_rss(source)
                elif source["type"] == "api":
                    policies = self._fetch_api(source)
                else:
                    policies = []
                all_policies.extend(policies)
                logger.info(f"Fetched {len(policies)} policies from {source['name']}")
            except Exception as e:
                logger.warning(f"Failed to fetch from {source['name']}: {e}")
        return all_policies

    def _fetch_rss(self, source: Dict) -> List[Dict]:
        try:
            feed = feedparser.parse(source["url"])
            return [
                {
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "source_url": entry.get("link", ""),
                    "source_name": source["name"],
                    "source_country": source["country"],
                    "announced_date": entry.get("published", datetime.utcnow().isoformat())[:10],
                    "status": "proposed",
                    "processed": False,
                }
                for entry in feed.entries[:20]
                if entry.get("title")
            ]
        except Exception as e:
            logger.warning(f"RSS parse failed: {e}")
            return []

    def _fetch_api(self, source: Dict) -> List[Dict]:
        """Fetch from API source."""
        return []  # Implement per-source

    def save_policy(self, policy: Dict) -> bool:
        """Save policy to DB (placeholder)."""
        logger.debug(f"Would save policy: {policy.get('title', '')[:50]}")
        return True
