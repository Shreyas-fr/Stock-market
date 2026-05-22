from fastapi import APIRouter, Depends, Query, HTTPException
from app.db.neo4j_db import neo4j_service
from app.db.redis_db import redis_service
from app.config import settings
from typing import Optional

router = APIRouter(prefix="/graph", tags=["Supply Chain Graph"])


@router.get("/{ticker}/nodes")
async def get_graph_nodes(
    ticker: str,
    depth: int = Query(2, ge=1, le=4),
):
    cache_key = f"graph:{ticker.upper()}:{depth}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached

    ticker = ticker.upper()

    # Get supplier nodes
    suppliers = await neo4j_service.query(
        """
        MATCH path = (target:Company {ticker: $ticker})<-[:SUPPLIES*1..$depth]-(supplier:Company)
        RETURN DISTINCT
            supplier.id AS id,
            supplier.ticker AS ticker,
            supplier.name AS name,
            supplier.sector AS sector,
            supplier.country AS country,
            supplier.riskScore AS risk_score,
            supplier.marketCap AS market_cap,
            length(path) AS tier
        ORDER BY tier, supplier.riskScore DESC
        """,
        {"ticker": ticker, "depth": depth},
    )

    # Get customer nodes
    customers = await neo4j_service.query(
        """
        MATCH (target:Company {ticker: $ticker})-[:SUPPLIES*1..2]->(customer:Company)
        RETURN DISTINCT
            customer.id AS id,
            customer.ticker AS ticker,
            customer.name AS name,
            customer.sector AS sector,
            customer.country AS country,
            customer.riskScore AS risk_score,
            customer.marketCap AS market_cap,
            1 AS tier
        """,
        {"ticker": ticker},
    )

    # Get the target company itself
    target = await neo4j_service.query(
        "MATCH (c:Company {ticker: $ticker}) RETURN c.id AS id, c.ticker AS ticker, c.name AS name, c.sector AS sector, c.country AS country, c.riskScore AS risk_score, c.marketCap AS market_cap",
        {"ticker": ticker},
    )

    # Get relationships
    relationships = await neo4j_service.query(
        """
        MATCH (supplier:Company)-[r:SUPPLIES]->(buyer:Company)
        WHERE supplier.ticker IN $supplier_tickers OR buyer.ticker = $ticker
        RETURN
            supplier.ticker AS source,
            buyer.ticker AS target,
            r.product AS product,
            r.shareOfCOGS AS share_of_cogs,
            r.contractType AS contract_type,
            r.confidence AS confidence
        """,
        {
            "supplier_tickers": [s["ticker"] for s in suppliers],
            "ticker": ticker,
        },
    )

    nodes = []
    if target:
        nodes.append({**target[0], "type": "target", "tier": 0})
    for s in suppliers:
        nodes.append({**s, "type": "supplier"})
    for c in customers:
        nodes.append({**c, "type": "customer"})

    result = {"nodes": nodes, "edges": relationships}
    await redis_service.set(cache_key, result, ttl=settings.cache_ttl_graph)
    return result


@router.get("/{ticker}/concentration-risk")
async def get_concentration_risk(ticker: str):
    """Geographic and single-source concentration risk"""
    geo_risk = await neo4j_service.query(
        """
        MATCH (company:Company {ticker: $ticker})<-[:SUPPLIES*1..2]-(supplier:Company)
              -[:HEADQUARTERED_IN]->(country:Country)
        RETURN country.name AS country, count(supplier) AS supplier_count
        ORDER BY supplier_count DESC
        """,
        {"ticker": ticker.upper()},
    )

    sole_source = await neo4j_service.query(
        """
        MATCH (company:Company {ticker: $ticker})<-[r:SUPPLIES]-(supplier:Company)
        WHERE r.contractType = 'sole-source' OR r.shareOfCOGS > 0.3
        RETURN
            supplier.ticker AS ticker,
            supplier.name AS name,
            r.product AS product,
            r.shareOfCOGS AS share_of_cogs,
            r.contractType AS contract_type
        ORDER BY r.shareOfCOGS DESC
        """,
        {"ticker": ticker.upper()},
    )

    return {
        "geographic_concentration": geo_risk,
        "high_dependency_suppliers": sole_source,
    }


@router.get("/{ticker}/impact")
async def get_policy_impact_on_graph(
    ticker: str,
    policy_id: Optional[str] = Query(None),
):
    """Show how a policy impacts the supply chain graph"""
    if not policy_id:
        return {"message": "Provide a policy_id to see impact"}

    impact = await neo4j_service.query(
        """
        MATCH (target:Company {ticker: $ticker})
        MATCH (p:Policy {id: $policy_id})-[:AFFECTS_SECTOR]->(s:Sector)
              <-[:BELONGS_TO]-(affected:Company)
        OPTIONAL MATCH (affected)<-[:SUPPLIES*1..3]-(supplier:Company)
        WITH affected, supplier, p
        WHERE affected.ticker = target.ticker OR EXISTS((affected)-[:SUPPLIES*1..3]->(target))
        RETURN DISTINCT
            coalesce(supplier.ticker, affected.ticker) AS ticker,
            coalesce(supplier.name, affected.name) AS name,
            coalesce(supplier.riskScore, affected.riskScore) AS risk_score,
            CASE WHEN supplier IS NULL THEN 'direct' ELSE 'indirect' END AS impact_type
        """,
        {"ticker": ticker.upper(), "policy_id": policy_id},
    )
    return {"impacted_nodes": impact}
