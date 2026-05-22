from celery_app import app
from crawlers.news_crawler import NewsCrawler
from loguru import logger
import os


@app.task(bind=True, max_retries=3)
def fetch_latest_news(self):
    """Fetch latest supply chain and financial news."""
    try:
        crawler = NewsCrawler(api_key=os.getenv("NEWSAPI_KEY"))
        
        queries = [
            "supply chain disruption",
            "semiconductor shortage",
            "lithium battery",
            "electric vehicle supply",
            "trade tariff",
            "government policy economy",
            "India manufacturing",
            "China export restriction",
        ]
        
        total = 0
        for query in queries:
            articles = crawler.fetch(query=query, page_size=10)
            if articles:
                crawler.save_articles(articles)
                total += len(articles)
        
        logger.info(f"Fetched {total} news articles")
        return {"status": "success", "articles_fetched": total}
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        raise self.retry(exc=e)


@app.task
def process_news_sentiment(article_id: str):
    """Process sentiment for a single article."""
    import httpx
    try:
        # Call AI service for sentiment
        response = httpx.post(
            "http://ai-service:8001/analyze/sentiment",
            json={"text": ""},  # article text would be fetched from DB
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Sentiment processing failed: {e}")
    return None
