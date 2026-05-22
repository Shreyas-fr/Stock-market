from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
import uuid
from app.db.postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(500), unique=True, nullable=False, index=True)
    name = Column(String(300))
    hashed_password = Column(String(200))
    role = Column(String(50), default="analyst")
    plan = Column(String(50), default="free")
    watchlist = Column(JSON)
    preferences = Column(JSON)
    api_key = Column(String(100), unique=True)
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash = Column(String(200), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
