from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.db.postgres import get_db
from app.db.redis_db import redis_service
from app.models.company import Company, StockPrice, FinancialStatement, FinancialMetric
from app.config import settings
from app.services.fmp_service import FMPService, normalise_statement
from typing import Optional, List
from pydantic import BaseModel
from loguru import logger
import uuid

router = APIRouter(prefix="/companies", tags=["Companies"])


class CompanyCreate(BaseModel):
    ticker: str
    name: str
    exchange: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None


@router.get("/search")
async def search_companies(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"search:{q}:{limit}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached
    
    stmt = select(Company).where(
        or_(
            func.lower(Company.name).contains(func.lower(q)),
            func.lower(Company.ticker).contains(func.lower(q)),
        )
    ).limit(limit)
    result = await db.execute(stmt)
    companies = result.scalars().all()
    
    data = [
        {
            "id": str(c.id),
            "ticker": c.ticker,
            "name": c.name,
            "exchange": c.exchange,
            "country": c.country,
            "sector": c.sector,
            "market_cap": float(c.market_cap) if c.market_cap else None,
            "logo_url": c.logo_url,
        }
        for c in companies
    ]
    
    await redis_service.set(cache_key, data, ttl=300)
    return data


@router.get("/{ticker}")
async def get_company(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"company:{ticker.upper()}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached
    
    result = await db.execute(select(Company).where(func.upper(Company.ticker) == ticker.upper()))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")
    
    data = {
        "id": str(company.id),
        "ticker": company.ticker,
        "name": company.name,
        "exchange": company.exchange,
        "country": company.country,
        "sector": company.sector,
        "industry": company.industry,
        "market_cap": float(company.market_cap) if company.market_cap else None,
        "employees": company.employees,
        "description": company.description,
        "website": company.website,
        "logo_url": company.logo_url,
        "founded_year": company.founded_year,
        "hq_city": company.hq_city,
        "hq_country": company.hq_country,
    }
    await redis_service.set(cache_key, data, ttl=settings.cache_ttl_company)
    return data


@router.post("/", status_code=201)
async def create_company(company_data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Company).where(func.upper(Company.ticker) == company_data.ticker.upper())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Company with this ticker already exists")
    
    company = Company(**company_data.model_dump())
    db.add(company)
    await db.flush()
    return {"id": str(company.id), "ticker": company.ticker, "name": company.name}


@router.get("/{ticker}/price-history")
async def get_price_history(
    ticker: str,
    days: int = Query(90, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"prices:{ticker.upper()}:{days}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached
    
    result = await db.execute(
        select(StockPrice)
        .where(func.upper(StockPrice.ticker) == ticker.upper())
        .order_by(StockPrice.date.desc())
        .limit(days)
    )
    prices = result.scalars().all()
    
    data = [
        {
            "date": p.date,
            "open": float(p.open) if p.open else None,
            "high": float(p.high) if p.high else None,
            "low": float(p.low) if p.low else None,
            "close": float(p.close) if p.close else None,
            "adj_close": float(p.adj_close) if p.adj_close else None,
            "volume": int(p.volume) if p.volume else None,
        }
        for p in reversed(prices)
    ]
    
    await redis_service.set(cache_key, data, ttl=settings.cache_ttl_prices)
    return data


@router.get("/{ticker}/financials")
async def get_financials(
    ticker: str,
    statement_type: str = Query("income", pattern="^(income|balance|cashflow)$"),
    period_type: str = Query("annual", pattern="^(annual|quarterly)$"),
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Return financial statements for a company.

    Strategy (fastest → slowest):
      1. Redis cache (TTL 1 h)
      2. PostgreSQL DB (persisted from previous FMP fetch)
      3. Live FMP API fetch → normalise → persist to DB → cache in Redis

    Supports any ticker that FMP recognises, including:
      - US equities  : AAPL, MSFT
      - Indian NSE   : RELIANCE.NS, TCS.NS
      - Indian BSE   : RELIANCE.BO
    """
    ticker_upper = ticker.upper()
    cache_key = f"financials:{ticker_upper}:{statement_type}:{period_type}:{limit}"

    # ── 1. Redis cache ──────────────────────────────────────────
    cached = await redis_service.get(cache_key)
    if cached:
        return cached

    # ── 2. Resolve company from DB ──────────────────────────────
    company_result = await db.execute(
        select(Company).where(func.upper(Company.ticker) == ticker_upper)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found in database. "
                   f"Seed it first via POST /api/v1/companies/",
        )

    # ── 3. Check PostgreSQL for existing statements ─────────────
    db_result = await db.execute(
        select(FinancialStatement)
        .where(
            FinancialStatement.company_id == company.id,
            FinancialStatement.statement_type == statement_type,
            FinancialStatement.period_type == period_type,
        )
        .order_by(FinancialStatement.period_end.desc())
        .limit(limit)
    )
    existing = db_result.scalars().all()

    if existing:
        data = _format_statements(existing, source="database")
        await redis_service.set(cache_key, data, ttl=settings.cache_ttl_company)
        return data

    # ── 4. Live fetch from FMP ──────────────────────────────────
    if not settings.fmp_api_key:
        raise HTTPException(
            status_code=503,
            detail="FMP_API_KEY is not configured. "
                   "Set it in your .env file to enable live financial data.",
        )

    logger.info(f"Fetching live FMP data: {ticker} | {statement_type} | {period_type}")
    fmp = FMPService(api_key=settings.fmp_api_key)
    raw_statements = await fmp.fetch_financials(
        ticker=ticker,            # FMP accepts RELIANCE.NS directly
        statement_type=statement_type,
        period_type=period_type,
        limit=limit,
    )

    if not raw_statements:
        raise HTTPException(
            status_code=404,
            detail=f"No {period_type} {statement_type} statements found for '{ticker}' "
                   f"on FMP. The ticker may not be covered by your FMP plan.",
        )

    # ── 5. Normalise + persist to DB ────────────────────────────
    persisted: list[FinancialStatement] = []
    for raw in raw_statements:
        try:
            period_end = raw.get("date", "")          # "2024-03-31"
            fiscal_year = int(period_end[:4]) if period_end else None
            fiscal_quarter_str = raw.get("period", "") # "Q1", "Q2", "FY"
            fiscal_quarter = None
            if fiscal_quarter_str.startswith("Q"):
                try:
                    fiscal_quarter = int(fiscal_quarter_str[1])
                except ValueError:
                    pass

            normalised = normalise_statement(statement_type, raw)

            stmt = FinancialStatement(
                id=uuid.uuid4(),
                company_id=company.id,
                period_type=period_type,
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
                period_end=period_end,
                currency=raw.get("reportedCurrency", "USD"),
                statement_type=statement_type,
                data=normalised,
                source="fmp",
                filing_url=raw.get("link"),
            )
            db.add(stmt)
            persisted.append(stmt)
        except Exception as e:
            logger.warning(f"Could not persist FMP statement for {ticker}: {e}")

    await db.flush()
    logger.info(f"Persisted {len(persisted)} FMP statements for {ticker} to DB")

    # ── 6. Format + cache + return ──────────────────────────────
    data = _format_statements(persisted, source="fmp_live")
    await redis_service.set(cache_key, data, ttl=settings.cache_ttl_company)
    return data


def _format_statements(statements, source: str) -> dict:
    """Serialise FinancialStatement ORM objects into the API response shape."""
    items = [
        {
            "fiscal_year":    s.fiscal_year,
            "fiscal_quarter": s.fiscal_quarter,
            "period_end":     s.period_end,
            "currency":       s.currency,
            "data":           s.data,
        }
        for s in statements
    ]
    return {
        "count":  len(items),
        "source": source,
        "statements": items,
    }

