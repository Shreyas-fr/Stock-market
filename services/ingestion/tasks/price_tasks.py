from celery_app import app
from crawlers.yahoo_finance import YahooFinanceCrawler
from crawlers.fmp_crawler import FMPCrawler
from loguru import logger
from typing import List
import os


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def update_stock_price(self, ticker: str):
    """Update stock price for a single ticker."""
    try:
        crawler = YahooFinanceCrawler()
        data = crawler.get_latest_price(ticker)
        if data:
            crawler.save_price(ticker, data)
            logger.info(f"Updated price for {ticker}: {data.get('close')}") 
        return {"ticker": ticker, "status": "success"}
    except Exception as e:
        logger.error(f"Price update failed for {ticker}: {e}")
        raise self.retry(exc=e)


@app.task
def update_all_prices():
    """Update prices for all tracked companies."""
    # Get tickers from DB or config
    TRACKED_TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META",
        "TSMC", "SAMSUNG", "TCS.NS", "INFY.NS", "RELIANCE.NS",
        "TATAMOTORS.NS", "MARUTI.NS", "BAJFINANCE.NS",
        "CATL.SZ", "BYD.SZ", "005930.KS",  # Samsung KRX
    ]
    
    for ticker in TRACKED_TICKERS:
        update_stock_price.delay(ticker)
    
    logger.info(f"Dispatched price updates for {len(TRACKED_TICKERS)} tickers")
    return {"dispatched": len(TRACKED_TICKERS)}


@app.task(bind=True, max_retries=2)
def update_financial_statements(self):
    """Update financial statements from FMP."""
    fmp_key = os.getenv("FMP_API_KEY")
    if not fmp_key:
        logger.warning("FMP_API_KEY not set, skipping financial statement update")
        return {"status": "skipped", "reason": "no_api_key"}
    
    try:
        crawler = FMPCrawler(api_key=fmp_key)
        TRACKED_TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        for ticker in TRACKED_TICKERS:
            crawler.fetch_income_statement(ticker)
            crawler.fetch_balance_sheet(ticker)
        return {"status": "success", "updated": len(TRACKED_TICKERS)}
    except Exception as e:
        logger.error(f"Financial statement update failed: {e}")
        raise self.retry(exc=e)
