from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time

from app.config import settings
from app.db.postgres import init_db
from app.db.neo4j_db import neo4j_service
from app.db.redis_db import redis_service
from app.db.elasticsearch_db import es_service
from app.routers import auth, companies, graph, policies, news, risk, ai_router, alerts
from app.websocket.hub import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Supply Chain Intelligence Platform API...")
    try:
        await redis_service.connect()
        logger.info("✓ Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    try:
        await neo4j_service.connect()
        await neo4j_service.init_schema()
        logger.info("✓ Neo4j connected and schema initialized")
    except Exception as e:
        logger.warning(f"Neo4j connection failed: {e}")

    try:
        await es_service.connect()
        await es_service.init_indices()
        logger.info("✓ Elasticsearch connected and indices initialized")
    except Exception as e:
        logger.warning(f"Elasticsearch connection failed: {e}")

    try:
        await init_db()
        logger.info("✓ PostgreSQL tables initialized")
    except Exception as e:
        logger.warning(f"PostgreSQL init failed: {e}")

    logger.info("✓ API startup complete")
    yield

    # Shutdown
    await neo4j_service.close()
    await redis_service.close()
    await es_service.close()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Supply Chain Intelligence Platform",
    description="AI-powered supply chain, financial, and government policy intelligence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.debug else "Contact support"},
    )


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "supply-chain-intelligence-api",
        "version": "1.0.0",
    }


# Include routers
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(companies.router, prefix=PREFIX)
app.include_router(graph.router, prefix=PREFIX)
app.include_router(policies.router, prefix=PREFIX)
app.include_router(news.router, prefix=PREFIX)
app.include_router(risk.router, prefix=PREFIX)
app.include_router(ai_router.router, prefix=PREFIX)
app.include_router(alerts.router, prefix=PREFIX)

# WebSocket
app.include_router(websocket_router)
