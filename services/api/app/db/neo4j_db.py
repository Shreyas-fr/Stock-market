from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import settings
from loguru import logger
from typing import Any, Dict, List, Optional


class Neo4jService:
    _driver: Optional[AsyncDriver] = None

    @classmethod
    async def connect(cls):
        cls._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        logger.info("Neo4j connected")

    @classmethod
    async def close(cls):
        if cls._driver:
            await cls._driver.close()

    @classmethod
    async def query(cls, cypher: str, params: Dict[str, Any] = None) -> List[Dict]:
        params = params or {}
        async with cls._driver.session() as session:
            result = await session.run(cypher, params)
            return [record.data() async for record in result]

    @classmethod
    async def execute(cls, cypher: str, params: Dict[str, Any] = None):
        params = params or {}
        async with cls._driver.session() as session:
            await session.run(cypher, params)

    @classmethod
    async def init_schema(cls):
        constraints = [
            "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT company_ticker IF NOT EXISTS FOR (c:Company) REQUIRE c.ticker IS UNIQUE",
            "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT sector_id IF NOT EXISTS FOR (s:Sector) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT country_code IF NOT EXISTS FOR (c:Country) REQUIRE c.code IS UNIQUE",
            "CREATE CONSTRAINT policy_id IF NOT EXISTS FOR (p:Policy) REQUIRE p.id IS UNIQUE",
        ]
        indexes = [
            "CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name)",
            "CREATE INDEX company_sector IF NOT EXISTS FOR (c:Company) ON (c.sector)",
            "CREATE INDEX company_country IF NOT EXISTS FOR (c:Company) ON (c.country)",
        ]
        for stmt in constraints + indexes:
            try:
                await cls.execute(stmt)
            except Exception as e:
                logger.warning(f"Schema stmt warning: {e}")
        logger.info("Neo4j schema initialized")


neo4j_service = Neo4jService()


async def get_neo4j():
    return neo4j_service
