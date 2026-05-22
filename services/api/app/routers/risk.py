from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.db.postgres import get_db
from app.db.redis_db import redis_service
from app.db.neo4j_db import neo4j_service
from app.models.risk import RiskScore
from app.models.company import Company
from app.config import settings
from typing import Optional

router = APIRouter(prefix="/risk", tags=["Risk Engine"])


@router.get("/{ticker}/score")
async def get_risk_score(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"risk:{ticker.upper()}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached

    company_result = await db.execute(
        select(Company).where(func.upper(Company.ticker) == ticker.upper())
    )
    company = company_result.scalar_one_or_none()
    if not company:
        return {"ticker": ticker, "error": "Company not found"}

    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.company_id == company.id)
        .order_by(desc(RiskScore.calculated_at))
        .limit(1)
    )
    score = result.scalar_one_or_none()

    if not score:
        return {
            "ticker": ticker,
            "overall_risk": 0.5,
            "supply_chain_risk": 0.5,
            "financial_risk": 0.5,
            "geopolitical_risk": 0.5,
            "regulatory_risk": 0.5,
            "market_risk": 0.5,
            "note": "Risk score not yet calculated",
        }

    data = {
        "ticker": ticker,
        "overall_risk": float(score.overall_risk) if score.overall_risk else None,
        "supply_chain_risk": float(score.supply_chain_risk) if score.supply_chain_risk else None,
        "financial_risk": float(score.financial_risk) if score.financial_risk else None,
        "geopolitical_risk": float(score.geopolitical_risk) if score.geopolitical_risk else None,
        "regulatory_risk": float(score.regulatory_risk) if score.regulatory_risk else None,
        "market_risk": float(score.market_risk) if score.market_risk else None,
        "risk_breakdown": score.risk_breakdown,
        "contributing_events": score.contributing_events,
        "calculated_at": score.calculated_at.isoformat() if score.calculated_at else None,
    }
    await redis_service.set(cache_key, data, ttl=settings.cache_ttl_risk_score)
    return data


@router.get("/{ticker}/history")
async def get_risk_history(
    ticker: str,
    days: int = Query(90, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    company_result = await db.execute(
        select(Company).where(func.upper(Company.ticker) == ticker.upper())
    )
    company = company_result.scalar_one_or_none()
    if not company:
        return []

    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.company_id == company.id)
        .order_by(desc(RiskScore.calculated_at))
        .limit(days)
    )
    scores = result.scalars().all()

    return [
        {
            "calculated_at": s.calculated_at.isoformat() if s.calculated_at else None,
            "overall_risk": float(s.overall_risk) if s.overall_risk else None,
            "supply_chain_risk": float(s.supply_chain_risk) if s.supply_chain_risk else None,
        }
        for s in reversed(scores)
    ]
