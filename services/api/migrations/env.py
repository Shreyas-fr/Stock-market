#!/usr/bin/env python3
"""
Alembic configuration for Supply Chain Intelligence Platform
"""
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all models to register them with Base
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.db.postgres import Base
from app.models.company import Company, StockPrice, FinancialStatement, FinancialMetric
from app.models.policy import GovernmentPolicy, NewsArticle
from app.models.risk import RiskScore, Alert, SupplyChainRelationship
from app.models.user import User, UserSession

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy URL from environment
database_url = os.getenv("DATABASE_URL_SYNC", "postgresql://sci_user:sci_password@localhost:5432/sci_db")
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
