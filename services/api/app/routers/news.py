from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.postgres import get_db
from app.db.elasticsearch_db import es_service
from app.models.policy import NewsArticle
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/news", tags=["News Intelligence"])


@router.get("/")
async def get_news(
    ticker: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(NewsArticle)
        .where(NewsArticle.published_at >= cutoff)
        .order_by(desc(NewsArticle.published_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    
    return [
        {
            "id": str(a.id),
            "headline": a.headline,
            "source_name": a.source_name,
            "source_url": a.source_url,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "categories": a.categories,
            "mentioned_companies": a.mentioned_companies,
            "sentiment_score": float(a.sentiment_score) if a.sentiment_score else None,
            "impact_score": float(a.impact_score) if a.impact_score else None,
        }
        for a in articles
    ]


@router.get("/search")
async def search_news(q: str = Query(..., min_length=2)):
    try:
        body = {
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["headline^3", "body"],
                }
            },
            "sort": [{"published_at": "desc"}],
            "size": 50,
        }
        response = await es_service.search(index="sci-news", body=body)
        hits = response.get("hits", {}).get("hits", [])
        return [{"id": h["_id"], **h["_source"]} for h in hits]
    except Exception as e:
        return {"error": str(e), "results": []}


@router.get("/sentiment-summary")
async def get_sentiment_summary(
    ticker: str = Query(...),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(NewsArticle)
        .where(NewsArticle.published_at >= cutoff)
        .where(NewsArticle.sentiment_score.isnot(None))
        .limit(200)
    )
    articles = result.scalars().all()
    
    if not articles:
        return {"ticker": ticker, "sentiment": "neutral", "score": 0, "article_count": 0}
    
    avg_sentiment = sum(float(a.sentiment_score) for a in articles) / len(articles)
    sentiment_label = "bullish" if avg_sentiment > 0.2 else "bearish" if avg_sentiment < -0.2 else "neutral"
    
    return {
        "ticker": ticker,
        "sentiment": sentiment_label,
        "score": round(avg_sentiment, 4),
        "article_count": len(articles),
        "days": days,
    }
