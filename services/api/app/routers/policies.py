from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.db.postgres import get_db
from app.db.redis_db import redis_service
from app.db.elasticsearch_db import es_service
from app.models.policy import GovernmentPolicy
from app.config import settings
from typing import Optional, List
from datetime import date, timedelta
import json

router = APIRouter(prefix="/policies", tags=["Government Policies"])


@router.get("/")
async def list_policies(
    sector: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    policy_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    days: Optional[int] = Query(30),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(GovernmentPolicy).order_by(desc(GovernmentPolicy.announced_date)).limit(limit).offset(offset)
    
    if sector:
        stmt = stmt.where(func.cast(GovernmentPolicy.affected_sectors, func.text).contains(sector))
    if country:
        stmt = stmt.where(GovernmentPolicy.source_country == country.upper())
    if policy_type:
        stmt = stmt.where(GovernmentPolicy.policy_type == policy_type)
    if status:
        stmt = stmt.where(GovernmentPolicy.status == status)
    
    result = await db.execute(stmt)
    policies = result.scalars().all()
    
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "summary": p.summary or p.ai_summary,
            "source_name": p.source_name,
            "source_country": p.source_country,
            "policy_type": p.policy_type,
            "status": p.status,
            "announced_date": p.announced_date,
            "affected_sectors": p.affected_sectors,
            "sentiment_score": float(p.sentiment_score) if p.sentiment_score else None,
            "impact_severity": p.impact_severity,
            "source_url": p.source_url,
        }
        for p in policies
    ]


@router.get("/recent")
async def get_recent_policies(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    result = await db.execute(
        select(GovernmentPolicy)
        .where(GovernmentPolicy.announced_date >= cutoff)
        .order_by(desc(GovernmentPolicy.announced_date))
        .limit(100)
    )
    policies = result.scalars().all()
    return [{"id": str(p.id), "title": p.title, "announced_date": p.announced_date, "impact_severity": p.impact_severity, "source_name": p.source_name} for p in policies]


@router.get("/search")
async def search_policies(q: str = Query(..., min_length=2)):
    try:
        body = {
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["title^3", "summary^2", "full_text"],
                }
            },
            "size": 50,
        }
        response = await es_service.search(index="sci-policies", body=body)
        hits = response.get("hits", {}).get("hits", [])
        return [{"id": h["_id"], **h["_source"]} for h in hits]
    except Exception as e:
        return {"error": str(e), "results": []}


@router.get("/{policy_id}")
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID
    try:
        uid = UUID(policy_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid policy ID")
    
    result = await db.execute(select(GovernmentPolicy).where(GovernmentPolicy.id == uid))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return {
        "id": str(policy.id),
        "title": policy.title,
        "summary": policy.summary,
        "full_text": policy.full_text,
        "ai_summary": policy.ai_summary,
        "source_name": policy.source_name,
        "source_url": policy.source_url,
        "source_country": policy.source_country,
        "policy_type": policy.policy_type,
        "status": policy.status,
        "announced_date": policy.announced_date,
        "effective_date": policy.effective_date,
        "affected_sectors": policy.affected_sectors,
        "affected_companies": policy.affected_companies,
        "sentiment_score": float(policy.sentiment_score) if policy.sentiment_score else None,
        "impact_severity": policy.impact_severity,
    }
