from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.postgres import Base


class GovernmentPolicy(Base):
    __tablename__ = "government_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    full_text = Column(Text)
    source_url = Column(String(1000))
    source_name = Column(String(200), index=True)
    source_country = Column(String(3))
    policy_type = Column(String(100), index=True)
    status = Column(String(50), index=True)
    announced_date = Column(String(10), index=True)
    effective_date = Column(String(10))
    expiry_date = Column(String(10))
    affected_sectors = Column(JSON)
    affected_companies = Column(JSON)
    ai_summary = Column(Text)
    sentiment_score = Column(Numeric(5, 4))
    impact_severity = Column(String(20))
    embedding_id = Column(String(200))
    raw_data = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_policy_date", "announced_date"),
    )


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    headline = Column(Text, nullable=False)
    body = Column(Text)
    source_name = Column(String(200))
    source_url = Column(String(1000))
    author = Column(String(300))
    published_at = Column(DateTime(timezone=True), index=True)
    language = Column(String(10), default="en")
    categories = Column(JSON)
    mentioned_companies = Column(JSON)
    sentiment_score = Column(Numeric(5, 4))
    impact_score = Column(Numeric(5, 4))
    embedding_id = Column(String(200))
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
