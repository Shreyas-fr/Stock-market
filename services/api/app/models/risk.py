from sqlalchemy import Column, String, Numeric, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.postgres import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    overall_risk = Column(Numeric(5, 4))
    supply_chain_risk = Column(Numeric(5, 4))
    financial_risk = Column(Numeric(5, 4))
    geopolitical_risk = Column(Numeric(5, 4))
    regulatory_risk = Column(Numeric(5, 4))
    market_risk = Column(Numeric(5, 4))
    risk_breakdown = Column(JSON)
    contributing_events = Column(JSON)
    horizon = Column(String(20))
    model_version = Column(String(50))

    __table_args__ = (
        Index("idx_risk_company_date", "company_id", "calculated_at"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    company_id = Column(UUID(as_uuid=True), nullable=True)
    alert_type = Column(String(100))
    severity = Column(String(20))
    title = Column(String, nullable=False)
    message = Column(String)
    alert_metadata = Column("metadata", JSON)
    read = Column(String(5), default="false")
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    channels = Column(JSON)


class SupplyChainRelationship(Base):
    __tablename__ = "supply_chain_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    buyer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    product = Column(String(500))
    share_of_revenue = Column(Numeric(5, 4))
    share_of_cogs = Column(Numeric(5, 4))
    contract_type = Column(String(50))
    since_year = Column(String(4))
    confidence = Column(Numeric(5, 4))
    source = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_sc_supplier", "supplier_id"),
        Index("idx_sc_buyer", "buyer_id"),
    )
