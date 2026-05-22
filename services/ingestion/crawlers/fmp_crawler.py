import httpx
from loguru import logger
from typing import Optional, Dict, List


class FMPCrawler:
    """Financial Modeling Prep API crawler."""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        params = params or {}
        params["apikey"] = self.api_key
        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(f"{self.BASE_URL}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"FMP API error: {e}")
            return None

    def fetch_income_statement(self, ticker: str, period: str = "annual", limit: int = 5) -> List[Dict]:
        data = self._get(f"/income-statement/{ticker}", {"period": period, "limit": limit})
        if not data:
            return []
        logger.info(f"Fetched {len(data)} {period} income statements for {ticker}")
        return data

    def fetch_balance_sheet(self, ticker: str, period: str = "annual", limit: int = 5) -> List[Dict]:
        data = self._get(f"/balance-sheet-statement/{ticker}", {"period": period, "limit": limit})
        return data or []

    def fetch_cash_flow(self, ticker: str, period: str = "annual", limit: int = 5) -> List[Dict]:
        data = self._get(f"/cash-flow-statement/{ticker}", {"period": period, "limit": limit})
        return data or []

    def fetch_profile(self, ticker: str) -> Optional[Dict]:
        data = self._get(f"/profile/{ticker}")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def fetch_key_metrics(self, ticker: str) -> Optional[Dict]:
        data = self._get(f"/key-metrics-ttm/{ticker}")
        if data and isinstance(data, list):
            return data[0]
        return None
