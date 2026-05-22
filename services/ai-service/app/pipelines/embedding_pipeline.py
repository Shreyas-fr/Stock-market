from typing import List, Optional
from loguru import logger


class EmbeddingPipeline:
    """Text embedding pipeline using sentence-transformers."""
    
    _model = None
    _initialized = False

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformer model...")
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Sentence transformer loaded")
        except Exception as e:
            logger.warning(f"sentence-transformers load failed: {e}")
            cls._model = None
        cls._initialized = True

    @classmethod
    def embed(cls, text: str) -> List[float]:
        if not cls._initialized:
            cls.initialize()
        if cls._model:
            try:
                embedding = cls._model.encode(text[:512])
                return embedding.tolist()
            except Exception as e:
                logger.warning(f"Embedding failed: {e}")
        # Fallback: zero vector
        return [0.0] * 384

    @classmethod
    def embed_batch(cls, texts: List[str]) -> List[List[float]]:
        if not cls._initialized:
            cls.initialize()
        if cls._model:
            try:
                embeddings = cls._model.encode(texts, batch_size=32)
                return [e.tolist() for e in embeddings]
            except Exception as e:
                logger.warning(f"Batch embedding failed: {e}")
        return [[0.0] * 384 for _ in texts]
