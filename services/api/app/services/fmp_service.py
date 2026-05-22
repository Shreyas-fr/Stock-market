"""
FMP (Financial Modeling Prep) async client for the API service.
Fetches real income statements, balance sheets, and cash flow statements.
"""
import httpx
from loguru import logger
from typing import Optional, Dict, List, Any


class FMPService:
    """Async FMP API client used directly by the FastAPI routers."""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    # Map our internal statement_type names → FMP endpoint paths
    ENDPOINTS = {
        "income":   "/income-statement/{ticker}",
        "balance":  "/balance-sheet-statement/{ticker}",
        "cashflow": "/cash-flow-statement/{ticker}",
    }

    # Map our period_type names → FMP period param values
    PERIOD_MAP = {
        "annual":    "annual",
        "quarterly": "quarter",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _get(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        params = params or {}
        params["apikey"] = self.api_key
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{self.BASE_URL}{endpoint}", params=params)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            logger.warning(f"FMP HTTP {e.response.status_code} for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"FMP request error for {endpoint}: {e}")
            return None

    async def fetch_financials(
        self,
        ticker: str,
        statement_type: str = "income",
        period_type: str = "annual",
        limit: int = 8,
    ) -> List[Dict]:
        """
        Fetch financial statements from FMP.
        Returns a list of raw FMP statement dicts, newest first.
        """
        endpoint_tmpl = self.ENDPOINTS.get(statement_type)
        if not endpoint_tmpl:
            return []

        endpoint = endpoint_tmpl.format(ticker=ticker)
        period = self.PERIOD_MAP.get(period_type, "annual")
        data = await self._get(endpoint, {"period": period, "limit": limit})

        if not data or not isinstance(data, list):
            logger.warning(f"FMP returned no data for {ticker} {statement_type} {period_type}")
            return []

        logger.info(f"FMP: fetched {len(data)} {period_type} {statement_type} records for {ticker}")
        return data

    async def fetch_key_metrics(self, ticker: str) -> Optional[Dict]:
        """Fetch trailing-12-month key metrics (PE, PB, ROE, etc.)."""
        data = await self._get(f"/key-metrics-ttm/{ticker}")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None


def _normalise_income(raw: Dict) -> Dict:
    """Map FMP income statement fields to our canonical schema."""
    return {
        "revenue":                  raw.get("revenue"),
        "cost_of_revenue":          raw.get("costOfRevenue"),
        "gross_profit":             raw.get("grossProfit"),
        "gross_profit_margin":      raw.get("grossProfitRatio"),
        "operating_expenses":       raw.get("operatingExpenses"),
        "operating_income":         raw.get("operatingIncome"),
        "operating_income_margin":  raw.get("operatingIncomeRatio"),
        "ebitda":                   raw.get("ebitda"),
        "ebitda_margin":            raw.get("ebitdaratio"),
        "net_income":               raw.get("netIncome"),
        "net_income_margin":        raw.get("netIncomeRatio"),
        "eps":                      raw.get("eps"),
        "eps_diluted":              raw.get("epsdiluted"),
        "shares_outstanding":       raw.get("weightedAverageShsOut"),
        "interest_expense":         raw.get("interestExpense"),
        "income_tax_expense":       raw.get("incomeTaxExpense"),
        "rd_expenses":              raw.get("researchAndDevelopmentExpenses"),
        "sga_expenses":             raw.get("sellingGeneralAndAdministrativeExpenses"),
        "depreciation_amortization": raw.get("depreciationAndAmortization"),
    }


def _normalise_balance(raw: Dict) -> Dict:
    """Map FMP balance sheet fields to our canonical schema."""
    return {
        "cash_and_equivalents":          raw.get("cashAndCashEquivalents"),
        "short_term_investments":        raw.get("shortTermInvestments"),
        "net_receivables":               raw.get("netReceivables"),
        "inventory":                     raw.get("inventory"),
        "total_current_assets":          raw.get("totalCurrentAssets"),
        "total_non_current_assets":      raw.get("totalNonCurrentAssets"),
        "total_assets":                  raw.get("totalAssets"),
        "total_current_liabilities":     raw.get("totalCurrentLiabilities"),
        "total_non_current_liabilities": raw.get("totalNonCurrentLiabilities"),
        "total_liabilities":             raw.get("totalLiabilities"),
        "total_stockholders_equity":     raw.get("totalStockholdersEquity"),
        "total_equity":                  raw.get("totalEquity"),
        "short_term_debt":               raw.get("shortTermDebt"),
        "long_term_debt":                raw.get("longTermDebt"),
        "total_debt":                    raw.get("totalDebt"),
        "net_debt":                      raw.get("netDebt"),
        "goodwill":                      raw.get("goodwill"),
        "intangible_assets":             raw.get("intangibleAssets"),
        "retained_earnings":             raw.get("retainedEarnings"),
    }


def _normalise_cashflow(raw: Dict) -> Dict:
    """Map FMP cash flow statement fields to our canonical schema."""
    return {
        "operating_cash_flow":             raw.get("operatingCashFlow"),
        "capital_expenditure":             raw.get("capitalExpenditure"),
        "free_cash_flow":                  raw.get("freeCashFlow"),
        "investing_cash_flow":             raw.get("netCashUsedForInvestingActivites"),
        "financing_cash_flow":             raw.get("netCashUsedProvidedByFinancingActivities"),
        "net_change_in_cash":              raw.get("netChangeInCash"),
        "depreciation_amortization":       raw.get("depreciationAndAmortization"),
        "stock_based_compensation":        raw.get("stockBasedCompensation"),
        "dividends_paid":                  raw.get("dividendsPaid"),
        "common_stock_repurchased":        raw.get("commonStockRepurchased"),
        "debt_repayment":                  raw.get("debtRepayment"),
        "acquisitions":                    raw.get("acquisitionsNet"),
        "purchases_of_investments":        raw.get("purchasesOfInvestments"),
    }


NORMALISERS = {
    "income":   _normalise_income,
    "balance":  _normalise_balance,
    "cashflow": _normalise_cashflow,
}


def normalise_statement(statement_type: str, raw: Dict) -> Dict:
    """Convert a raw FMP statement dict into our canonical field names."""
    fn = NORMALISERS.get(statement_type, lambda x: x)
    return fn(raw)
