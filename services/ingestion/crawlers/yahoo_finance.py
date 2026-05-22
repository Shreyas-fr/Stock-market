import yfinance as yf
from datetime import datetime, date
from loguru import logger
from typing import Optional, Dict, List


class YahooFinanceCrawler:
    """Fetches stock prices from Yahoo Finance (free tier)."""

    def get_latest_price(self, ticker: str) -> Optional[Dict]:
        """Get the latest price data for a ticker."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if hist.empty:
                return None
            latest = hist.iloc[-1]
            return {
                "ticker": ticker,
                "date": hist.index[-1].strftime("%Y-%m-%d"),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "close": float(latest["Close"]),
                "volume": int(latest["Volume"]),
                "source": "yahoo_finance",
            }
        except Exception as e:
            logger.error(f"Yahoo Finance error for {ticker}: {e}")
            return None

    def get_price_history(self, ticker: str, period: str = "1y") -> List[Dict]:
        """Get historical price data."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return []
            return [
                {
                    "ticker": ticker,
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "source": "yahoo_finance",
                }
                for idx, row in hist.iterrows()
            ]
        except Exception as e:
            logger.error(f"Yahoo Finance history error for {ticker}: {e}")
            return []

    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get company info."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName", ticker),
                "exchange": info.get("exchange"),
                "country": info.get("country"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "employees": info.get("fullTimeEmployees"),
                "description": info.get("longBusinessSummary"),
                "website": info.get("website"),
                "hq_city": info.get("city"),
                "hq_country": info.get("country"),
            }
        except Exception as e:
            logger.error(f"Yahoo Finance company info error for {ticker}: {e}")
            return None

    def save_price(self, ticker: str, data: Dict):
        """Save price to DB (placeholder - would use SQLAlchemy)."""
        logger.debug(f"Would save price for {ticker}: {data['close']}")
