from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Any
import json


class Settings(BaseSettings):
    # App
    app_name: str = "Supply Chain Intelligence Platform"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    database_url: str = "postgresql+asyncpg://sci_user:sci_password@postgres:5432/sci_db"
    database_url_sync: str = "postgresql://sci_user:sci_password@postgres:5432/sci_db"

    # Neo4j
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "sci_password"

    # Redis
    redis_url: str = "redis://:sci_password@redis:6379/0"
    celery_broker_url: str = "redis://:sci_password@redis:6379/1"
    celery_result_backend: str = "redis://:sci_password@redis:6379/2"

    # Elasticsearch
    elasticsearch_url: str = "http://elastic:sci_password@elasticsearch:9200"

    # AI APIs
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Financial APIs
    alpha_vantage_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    yahoo_finance_enabled: bool = True

    # News APIs
    newsapi_key: Optional[str] = None
    gnews_api_key: Optional[str] = None

    # JWT
    jwt_secret_key: str = "jwt-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Cache TTLs (seconds)
    cache_ttl_prices: int = 30
    cache_ttl_company: int = 3600
    cache_ttl_risk_score: int = 3600
    cache_ttl_news: int = 300
    cache_ttl_policies: int = 1800
    cache_ttl_graph: int = 7200

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Vector DB
    use_local_vector_db: bool = True
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sci-embeddings"

    # Monitoring
    log_level: str = "INFO"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> List[str]:
        """Accept JSON arrays, comma-separated strings, or plain lists."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            # Try JSON array first: ["a","b"]
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Fall back to comma-separated
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
