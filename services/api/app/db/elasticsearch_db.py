from elasticsearch import AsyncElasticsearch
from app.config import settings
from loguru import logger
from typing import Optional, Dict, List, Any


class ElasticsearchService:
    _client: Optional[AsyncElasticsearch] = None

    @classmethod
    async def connect(cls):
        cls._client = AsyncElasticsearch([settings.elasticsearch_url])
        info = await cls._client.info()
        logger.info(f"Elasticsearch connected: {info['version']['number']}")

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()

    @classmethod
    async def init_indices(cls):
        indices = {
            "sci-policies": {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "english"},
                        "summary": {"type": "text", "analyzer": "english"},
                        "full_text": {"type": "text", "analyzer": "english"},
                        "source_name": {"type": "keyword"},
                        "policy_type": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "announced_date": {"type": "date"},
                        "affected_sectors": {"type": "keyword"},
                        "sentiment_score": {"type": "float"},
                        "impact_severity": {"type": "keyword"},
                    }
                }
            },
            "sci-news": {
                "mappings": {
                    "properties": {
                        "headline": {"type": "text", "analyzer": "english"},
                        "body": {"type": "text", "analyzer": "english"},
                        "source_name": {"type": "keyword"},
                        "published_at": {"type": "date"},
                        "sentiment_score": {"type": "float"},
                        "impact_score": {"type": "float"},
                        "categories": {"type": "keyword"},
                    }
                }
            },
            "sci-companies": {
                "mappings": {
                    "properties": {
                        "name": {"type": "text", "analyzer": "english"},
                        "ticker": {"type": "keyword"},
                        "sector": {"type": "keyword"},
                        "country": {"type": "keyword"},
                        "description": {"type": "text"},
                    }
                }
            },
        }
        for index_name, body in indices.items():
            exists = await cls._client.indices.exists(index=index_name)
            if not exists:
                await cls._client.indices.create(index=index_name, body=body)
                logger.info(f"Created ES index: {index_name}")

    @classmethod
    async def search(cls, index: str, body: Dict) -> Dict:
        return await cls._client.search(index=index, body=body)

    @classmethod
    async def index_doc(cls, index: str, doc_id: str, doc: Dict):
        await cls._client.index(index=index, id=doc_id, document=doc)

    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        return cls._client


es_service = ElasticsearchService()


async def get_es():
    return es_service
