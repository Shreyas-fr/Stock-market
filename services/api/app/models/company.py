from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.postgres import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    isin = Column(String(20))
    cusip = Column(String(9))
    exchange = Column(String(50))
    country = Column(String(3), index=True)
    sector = Column(String(200), index=True)
    industry = Column(String(200))
    market_cap = Column(Numeric(20, 2))
    employees = Column(Integer)
    description = Column(Text)
    website = Column(String(500))
    logo_url = Column(String(500))
    founded_year = Column(Integer)
    hq_city = Column(String(200))
    hq_country = Column(String(200))
    data_sources = Column(JSON)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_companies_name", "name"),
    )


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    open = Column(Numeric(15, 4))
    high = Column(Numeric(15, 4))
    low = Column(Numeric(15, 4))
    close = Column(Numeric(15, 4))
    adj_close = Column(Numeric(15, 4))
    volume = Column(Numeric(20, 0))
    source = Column(String(100))

    __table_args__ = (
        Index("idx_sp_company_date", "company_id", "date"),
        Index("idx_sp_ticker_date", "ticker", "date"),
    )


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    period_type = Column(String(10), nullable=False)  # annual | quarterly
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)
    period_end = Column(String(10), nullable=False)  # YYYY-MM-DD
    currency = Column(String(3), default="USD")
    statement_type = Column(String(30), nullable=False)  # income | balance | cashflow
    data = Column(JSON, nullable=False)
    source = Column(String(100))
    filing_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_fs_company_period", "company_id", "period_end"),
    )


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(String(10), nullable=False)
    pe_ratio = Column(Numeric(10, 4))
    pb_ratio = Column(Numeric(10, 4))
    ps_ratio = Column(Numeric(10, 4))
    ev_ebitda = Column(Numeric(10, 4))
    debt_to_equity = Column(Numeric(10, 4))
    current_ratio = Column(Numeric(10, 4))
    quick_ratio = Column(Numeric(10, 4))
    roe = Column(Numeric(10, 4))
    roa = Column(Numeric(10, 4))
    roic = Column(Numeric(10, 4))
    free_cash_flow = Column(Numeric(20, 2))
    dividend_yield = Column(Numeric(10, 4))
    beta = Column(Numeric(8, 4))
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
