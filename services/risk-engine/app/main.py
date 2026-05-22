from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Risk Engine Service...")
    yield
    logger.info("Risk Engine shutdown")


app = FastAPI(
    title="Supply Chain Risk Engine",
    description="Risk scoring and impact propagation service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "risk-engine"}


@app.post("/calculate/{company_id}")
async def calculate_risk(company_id: str):
    from app.calculators.composite_risk import CompositeRiskCalculator
    calc = CompositeRiskCalculator()
    result = await calc.calculate(company_id)
    return result


@app.post("/propagate")
async def propagate_impact(payload: dict):
    from app.propagation.graph_propagator import GraphPropagator
    policy_id = payload.get("policy_id")
    propagator = GraphPropagator()
    result = await propagator.propagate(policy_id)
    return result
