from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import httpx
import json
from app.config import settings
from app.db.redis_db import redis_service
from loguru import logger

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


class PolicyImpactRequest(BaseModel):
    policy_text: str
    target_sectors: Optional[List[str]] = None
    target_ticker: Optional[str] = None


class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = 200


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    company_context: Optional[str] = None


async def call_openai(messages: list, model: str = None) -> str:
    if not settings.openai_api_key:
        return "OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file."
    
    model = model or settings.openai_model
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={"model": model, "messages": messages, "temperature": 0.3},
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


@router.post("/policy-impact")
async def analyze_policy_impact(req: PolicyImpactRequest):
    """AI-powered policy impact analysis"""
    sectors_str = ", ".join(req.target_sectors) if req.target_sectors else "general economy"
    
    prompt = f"""You are a senior financial analyst specializing in supply chain and regulatory impact.

POLICY TEXT:
{req.policy_text[:3000]}

TARGET SECTORS: {sectors_str}
{f'TARGET COMPANY: {req.target_ticker}' if req.target_ticker else ''}

Analyze the impact of this policy. Provide a JSON response with:
{{
  "policy_type": "tariff/regulation/subsidy/ban/other",
  "affected_sectors": ["..."],
  "direct_impact": "...",
  "supply_chain_impact": "...",
  "stock_direction": "BULLISH/BEARISH/NEUTRAL",
  "confidence": "LOW/MEDIUM/HIGH",
  "time_horizon": "IMMEDIATE/3-MONTH/12-MONTH",
  "margin_change_estimate_pct": 0.0,
  "summary": "2-3 sentence dashboard summary",
  "risk_level": "low/medium/high/critical"
}}

Respond ONLY with valid JSON."""
    
    try:
        content = await call_openai([{"role": "user", "content": prompt}])
        # Try to parse as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Extract JSON from markdown code blocks
            import re
            match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return {"summary": content, "raw": True}
    except Exception as e:
        logger.error(f"Policy impact analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_text(req: SummarizeRequest):
    """Summarize a document or text snippet"""
    prompt = f"""Summarize the following text in {req.max_length} words or less.
Focus on financial and supply chain implications.

TEXT:
{req.text[:5000]}

Provide a concise, professional summary:"""
    
    try:
        summary = await call_openai([{"role": "user", "content": prompt}])
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def ai_chat(req: ChatRequest):
    """AI assistant for company and supply chain research"""
    system_prompt = """You are an expert financial and supply chain analyst with access to company data.
You help users understand supply chain risks, financial performance, and government policy impacts.
Be concise, data-driven, and highlight key risks and opportunities."""
    
    if req.company_context:
        system_prompt += f"\n\nCOMPANY CONTEXT:\n{req.company_context}"
    
    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in req.messages]
    
    try:
        response = await call_openai(messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-narrative/{ticker}")
async def get_risk_narrative(ticker: str):
    """Generate AI risk narrative for a company"""
    cache_key = f"ai:narrative:{ticker.upper()}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached
    
    prompt = f"""Generate a concise 3-paragraph risk narrative for {ticker.upper()} covering:
1. Current supply chain risks (geographic concentration, single-source dependencies)
2. Regulatory and geopolitical exposure
3. Financial health and market risk outlook

Base this on general knowledge of the company. Be specific and actionable."""
    
    try:
        narrative = await call_openai([{"role": "user", "content": prompt}])
        result = {"ticker": ticker.upper(), "narrative": narrative}
        await redis_service.set(cache_key, result, ttl=7200)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sector-outlook/{sector}")
async def get_sector_outlook(sector: str):
    """AI-generated sector outlook"""
    cache_key = f"ai:sector:{sector.lower()}"
    cached = await redis_service.get(cache_key)
    if cached:
        return cached
    
    prompt = f"""Provide a structured outlook for the {sector} sector covering:
- Current supply chain dynamics
- Key regulatory risks
- Geopolitical exposure
- Demand outlook
- Top 3 risks and opportunities

Format as structured JSON with keys: supply_chain, regulatory, geopolitical, demand, risks, opportunities, overall_sentiment"""
    
    try:
        content = await call_openai([{"role": "user", "content": prompt}])
        try:
            result = json.loads(content)
        except:
            result = {"outlook": content}
        result["sector"] = sector
        await redis_service.set(cache_key, result, ttl=14400)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
