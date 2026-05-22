from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.pipelines.nlp_pipeline import NLPPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Service...")
    # Initialize NLP models
    try:
        NLPPipeline.initialize()
        logger.info("✓ NLP models loaded")
    except Exception as e:
        logger.warning(f"NLP models failed to load: {e}")
    yield
    logger.info("AI Service shutdown")


app = FastAPI(
    title="Supply Chain AI Service",
    description="NLP, embeddings, and AI inference service",
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
    return {"status": "healthy", "service": "ai-service"}


@app.post("/analyze/sentiment")
async def analyze_sentiment(payload: dict):
    from app.pipelines.nlp_pipeline import NLPPipeline
    text = payload.get("text", "")
    result = NLPPipeline.sentiment(text)
    return result


@app.post("/analyze/entities")
async def extract_entities(payload: dict):
    from app.pipelines.nlp_pipeline import NLPPipeline
    text = payload.get("text", "")
    result = NLPPipeline.extract_entities(text)
    return {"entities": result}


@app.post("/embed")
async def embed_text(payload: dict):
    from app.pipelines.embedding_pipeline import EmbeddingPipeline
    text = payload.get("text", "")
    embedding = EmbeddingPipeline.embed(text)
    return {"embedding": embedding, "dim": len(embedding)}
