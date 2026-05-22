#!/usr/bin/env python3
"""
Seed script: Inserts 50 major companies into PostgreSQL and Neo4j.
Run: python scripts/seed_companies.py
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sci_user:sci_password@localhost:5432/sci_db")

COMPANIES = [
    # Tech Giants
    {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 2900000000000, "employees": 164000, "hq_city": "Cupertino", "hq_country": "USA", "founded_year": 1976, "website": "https://apple.com", "logo_url": "https://logo.clearbit.com/apple.com"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Software", "market_cap": 3200000000000, "employees": 220000, "hq_city": "Redmond", "hq_country": "USA", "founded_year": 1975, "website": "https://microsoft.com", "logo_url": "https://logo.clearbit.com/microsoft.com"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Internet Services", "market_cap": 2100000000000, "employees": 182000, "hq_city": "Mountain View", "hq_country": "USA", "founded_year": 1998, "website": "https://alphabet.com", "logo_url": "https://logo.clearbit.com/google.com"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Consumer Discretionary", "industry": "E-Commerce", "market_cap": 2000000000000, "employees": 1500000, "hq_city": "Seattle", "hq_country": "USA", "founded_year": 1994, "website": "https://amazon.com", "logo_url": "https://logo.clearbit.com/amazon.com"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Semiconductors", "market_cap": 2500000000000, "employees": 32000, "hq_city": "Santa Clara", "hq_country": "USA", "founded_year": 1993, "website": "https://nvidia.com", "logo_url": "https://logo.clearbit.com/nvidia.com"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Consumer Discretionary", "industry": "Electric Vehicles", "market_cap": 700000000000, "employees": 140000, "hq_city": "Austin", "hq_country": "USA", "founded_year": 2003, "website": "https://tesla.com", "logo_url": "https://logo.clearbit.com/tesla.com"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Social Media", "market_cap": 1400000000000, "employees": 67000, "hq_city": "Menlo Park", "hq_country": "USA", "founded_year": 2004, "website": "https://meta.com", "logo_url": "https://logo.clearbit.com/meta.com"},
    
    # Semiconductors
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing", "exchange": "NYSE", "country": "TWN", "sector": "Technology", "industry": "Semiconductors", "market_cap": 550000000000, "employees": 73000, "hq_city": "Hsinchu", "hq_country": "TWN", "founded_year": 1987, "website": "https://tsmc.com", "logo_url": "https://logo.clearbit.com/tsmc.com"},
    {"ticker": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Semiconductors", "market_cap": 100000000000, "employees": 120000, "hq_city": "Santa Clara", "hq_country": "USA", "founded_year": 1968, "website": "https://intel.com", "logo_url": "https://logo.clearbit.com/intel.com"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Semiconductors", "market_cap": 250000000000, "employees": 26000, "hq_city": "Santa Clara", "hq_country": "USA", "founded_year": 1969, "website": "https://amd.com", "logo_url": "https://logo.clearbit.com/amd.com"},
    {"ticker": "QCOM", "name": "Qualcomm Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Semiconductors", "market_cap": 200000000000, "employees": 51000, "hq_city": "San Diego", "hq_country": "USA", "founded_year": 1985, "website": "https://qualcomm.com", "logo_url": "https://logo.clearbit.com/qualcomm.com"},
    {"ticker": "AMAT", "name": "Applied Materials Inc.", "exchange": "NASDAQ", "country": "USA", "sector": "Technology", "industry": "Semiconductor Equipment", "market_cap": 150000000000, "employees": 34000, "hq_city": "Santa Clara", "hq_country": "USA", "founded_year": 1967, "website": "https://appliedmaterials.com", "logo_url": "https://logo.clearbit.com/appliedmaterials.com"},
    
    # Automotive / EV
    {"ticker": "TM", "name": "Toyota Motor Corporation", "exchange": "NYSE", "country": "JPN", "sector": "Consumer Discretionary", "industry": "Automotive", "market_cap": 300000000000, "employees": 375000, "hq_city": "Toyota", "hq_country": "JPN", "founded_year": 1937, "website": "https://toyota.com", "logo_url": "https://logo.clearbit.com/toyota.com"},
    {"ticker": "RIVN", "name": "Rivian Automotive", "exchange": "NASDAQ", "country": "USA", "sector": "Consumer Discretionary", "industry": "Electric Vehicles", "market_cap": 15000000000, "employees": 14000, "hq_city": "Irvine", "hq_country": "USA", "founded_year": 2009, "website": "https://rivian.com", "logo_url": "https://logo.clearbit.com/rivian.com"},
    
    # Indian Companies
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services", "exchange": "NSE", "country": "IND", "sector": "Technology", "industry": "IT Services", "market_cap": 160000000000, "employees": 600000, "hq_city": "Mumbai", "hq_country": "IND", "founded_year": 1968, "website": "https://tcs.com", "logo_url": "https://logo.clearbit.com/tcs.com"},
    {"ticker": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE", "country": "IND", "sector": "Technology", "industry": "IT Services", "market_cap": 70000000000, "employees": 343000, "hq_city": "Bengaluru", "hq_country": "IND", "founded_year": 1981, "website": "https://infosys.com", "logo_url": "https://logo.clearbit.com/infosys.com"},
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries Limited", "exchange": "NSE", "country": "IND", "sector": "Energy", "industry": "Oil & Gas Refining", "market_cap": 220000000000, "employees": 236000, "hq_city": "Mumbai", "hq_country": "IND", "founded_year": 1966, "website": "https://ril.com", "logo_url": "https://logo.clearbit.com/ril.com"},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Limited", "exchange": "NSE", "country": "IND", "sector": "Consumer Discretionary", "industry": "Automotive", "market_cap": 28000000000, "employees": 84000, "hq_city": "Mumbai", "hq_country": "IND", "founded_year": 1945, "website": "https://tatamotors.com", "logo_url": "https://logo.clearbit.com/tatamotors.com"},
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India", "exchange": "NSE", "country": "IND", "sector": "Consumer Discretionary", "industry": "Automotive", "market_cap": 50000000000, "employees": 23000, "hq_city": "New Delhi", "hq_country": "IND", "founded_year": 1981, "website": "https://marutisuzuki.com", "logo_url": "https://logo.clearbit.com/marutisuzuki.com"},
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE", "country": "IND", "sector": "Financials", "industry": "Consumer Finance", "market_cap": 45000000000, "employees": 40000, "hq_city": "Pune", "hq_country": "IND", "founded_year": 1987, "website": "https://bajajfinserv.in", "logo_url": "https://logo.clearbit.com/bajajfinserv.in"},
    {"ticker": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE", "country": "IND", "sector": "Technology", "industry": "IT Services", "market_cap": 30000000000, "employees": 250000, "hq_city": "Bengaluru", "hq_country": "IND", "founded_year": 1945, "website": "https://wipro.com", "logo_url": "https://logo.clearbit.com/wipro.com"},
    
    # Electronics / Supply Chain
    {"ticker": "HON", "name": "Honeywell International", "exchange": "NASDAQ", "country": "USA", "sector": "Industrials", "industry": "Industrial Conglomerate", "market_cap": 130000000000, "employees": 96000, "hq_city": "Charlotte", "hq_country": "USA", "founded_year": 1906, "website": "https://honeywell.com", "logo_url": "https://logo.clearbit.com/honeywell.com"},
    {"ticker": "GE", "name": "GE Aerospace", "exchange": "NYSE", "country": "USA", "sector": "Industrials", "industry": "Aerospace & Defense", "market_cap": 180000000000, "employees": 160000, "hq_city": "Evendale", "hq_country": "USA", "founded_year": 1892, "website": "https://ge.com", "logo_url": "https://logo.clearbit.com/ge.com"},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "exchange": "NYSE", "country": "USA", "sector": "Industrials", "industry": "Construction Machinery", "market_cap": 170000000000, "employees": 111000, "hq_city": "Irving", "hq_country": "USA", "founded_year": 1925, "website": "https://caterpillar.com", "logo_url": "https://logo.clearbit.com/caterpillar.com"},
    
    # Battery / Energy Storage
    {"ticker": "LGES.KS", "name": "LG Energy Solution", "exchange": "KRX", "country": "KOR", "sector": "Technology", "industry": "Battery Manufacturing", "market_cap": 70000000000, "employees": 27000, "hq_city": "Seoul", "hq_country": "KOR", "founded_year": 2020, "website": "https://lgesolution.com", "logo_url": "https://logo.clearbit.com/lgesolution.com"},
    {"ticker": "PCRFY", "name": "Panasonic Holdings", "exchange": "OTC", "country": "JPN", "sector": "Technology", "industry": "Battery Manufacturing", "market_cap": 25000000000, "employees": 233000, "hq_city": "Osaka", "hq_country": "JPN", "founded_year": 1918, "website": "https://panasonic.net", "logo_url": "https://logo.clearbit.com/panasonic.com"},
    
    # Consumer Electronics
    {"ticker": "SONY", "name": "Sony Group Corporation", "exchange": "NYSE", "country": "JPN", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 120000000000, "employees": 108000, "hq_city": "Tokyo", "hq_country": "JPN", "founded_year": 1946, "website": "https://sony.com", "logo_url": "https://logo.clearbit.com/sony.com"},
    {"ticker": "SNE", "name": "Samsung Electronics", "exchange": "OTC", "country": "KOR", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 330000000000, "employees": 270000, "hq_city": "Suwon", "hq_country": "KOR", "founded_year": 1969, "website": "https://samsung.com", "logo_url": "https://logo.clearbit.com/samsung.com"},
    
    # Retail / E-Commerce
    {"ticker": "WMT", "name": "Walmart Inc.", "exchange": "NYSE", "country": "USA", "sector": "Consumer Staples", "industry": "Discount Retail", "market_cap": 600000000000, "employees": 2100000, "hq_city": "Bentonville", "hq_country": "USA", "founded_year": 1962, "website": "https://walmart.com", "logo_url": "https://logo.clearbit.com/walmart.com"},
    
    # Energy / Minerals
    {"ticker": "XOM", "name": "ExxonMobil Corporation", "exchange": "NYSE", "country": "USA", "sector": "Energy", "industry": "Oil & Gas", "market_cap": 500000000000, "employees": 62000, "hq_city": "Spring", "hq_country": "USA", "founded_year": 1870, "website": "https://exxonmobil.com", "logo_url": "https://logo.clearbit.com/exxonmobil.com"},
    {"ticker": "ALB", "name": "Albemarle Corporation", "exchange": "NYSE", "country": "USA", "sector": "Materials", "industry": "Lithium Mining", "market_cap": 10000000000, "employees": 7700, "hq_city": "Charlotte", "hq_country": "USA", "founded_year": 1994, "website": "https://albemarle.com", "logo_url": "https://logo.clearbit.com/albemarle.com"},
    
    # Pharma / Healthcare  
    {"ticker": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "country": "USA", "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": 400000000000, "employees": 152000, "hq_city": "New Brunswick", "hq_country": "USA", "founded_year": 1886, "website": "https://jnj.com", "logo_url": "https://logo.clearbit.com/jnj.com"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "exchange": "NYSE", "country": "USA", "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": 150000000000, "employees": 83000, "hq_city": "New York", "hq_country": "USA", "founded_year": 1849, "website": "https://pfizer.com", "logo_url": "https://logo.clearbit.com/pfizer.com"},
    
    # Logistics
    {"ticker": "FDX", "name": "FedEx Corporation", "exchange": "NYSE", "country": "USA", "sector": "Industrials", "industry": "Air Freight & Logistics", "market_cap": 60000000000, "employees": 547000, "hq_city": "Memphis", "hq_country": "USA", "founded_year": 1971, "website": "https://fedex.com", "logo_url": "https://logo.clearbit.com/fedex.com"},
    {"ticker": "UPS", "name": "United Parcel Service", "exchange": "NYSE", "country": "USA", "sector": "Industrials", "industry": "Air Freight & Logistics", "market_cap": 80000000000, "employees": 500000, "hq_city": "Atlanta", "hq_country": "USA", "founded_year": 1907, "website": "https://ups.com", "logo_url": "https://logo.clearbit.com/ups.com"},
]

SUPPLY_CHAIN_RELATIONSHIPS = [
    # Apple supply chain
    {"supplier": "TSM", "buyer": "AAPL", "product": "A-series chips", "share_of_cogs": 0.18, "contract_type": "sole-source", "confidence": 0.95, "source": "SEC-10K"},
    {"supplier": "QCOM", "buyer": "AAPL", "product": "5G modems", "share_of_cogs": 0.05, "contract_type": "multi-source", "confidence": 0.90, "source": "news"},
    {"supplier": "SONY", "buyer": "AAPL", "product": "CMOS image sensors", "share_of_cogs": 0.04, "contract_type": "sole-source", "confidence": 0.88, "source": "annual-report"},
    {"supplier": "SNE", "buyer": "AAPL", "product": "OLED displays", "share_of_cogs": 0.08, "contract_type": "multi-source", "confidence": 0.85, "source": "news"},
    
    # Tesla supply chain
    {"supplier": "PCRFY", "buyer": "TSLA", "product": "cylindrical battery cells", "share_of_cogs": 0.22, "contract_type": "multi-source", "confidence": 0.92, "source": "SEC-10K"},
    {"supplier": "ALB", "buyer": "TSLA", "product": "lithium hydroxide", "share_of_cogs": 0.06, "contract_type": "multi-source", "confidence": 0.88, "source": "news"},
    {"supplier": "LGES.KS", "buyer": "TSLA", "product": "NMC battery cells", "share_of_cogs": 0.15, "contract_type": "multi-source", "confidence": 0.90, "source": "SEC-10K"},
    
    # NVIDIA supply chain
    {"supplier": "TSM", "buyer": "NVDA", "product": "GPU wafers (3nm/4nm)", "share_of_cogs": 0.55, "contract_type": "sole-source", "confidence": 0.98, "source": "SEC-10K"},
    {"supplier": "SNE", "buyer": "NVDA", "product": "HBM memory", "share_of_cogs": 0.10, "contract_type": "multi-source", "confidence": 0.80, "source": "news"},
    
    # Tata Motors supply chain  
    {"supplier": "LGES.KS", "buyer": "TATAMOTORS.NS", "product": "EV battery packs", "share_of_cogs": 0.28, "contract_type": "multi-source", "confidence": 0.85, "source": "annual-report"},
    
    # Intel
    {"supplier": "AMAT", "buyer": "INTC", "product": "wafer fabrication equipment", "share_of_cogs": 0.12, "contract_type": "multi-source", "confidence": 0.82, "source": "SEC-10K"},
    {"supplier": "AMAT", "buyer": "TSM", "product": "deposition and etch equipment", "share_of_cogs": 0.15, "contract_type": "multi-source", "confidence": 0.90, "source": "SEC-10K"},
]

SEED_POLICIES = [
    {
        "title": "India Reduces Lithium Battery Import Duty to 5%",
        "summary": "The Indian government has reduced import duty on lithium-ion batteries from 18% to 5% to boost electric vehicle adoption and domestic manufacturing.",
        "source_name": "PIB India",
        "source_country": "IND",
        "policy_type": "tariff_reduction",
        "status": "enacted",
        "announced_date": "2024-02-01",
        "effective_date": "2024-04-01",
        "affected_sectors": ["Electric Vehicles", "Consumer Electronics", "Energy Storage"],
        "sentiment_score": 0.75,
        "impact_severity": "high",
    },
    {
        "title": "US CHIPS Act: $52B Semiconductor Manufacturing Subsidies",
        "summary": "The CHIPS and Science Act provides $52 billion in subsidies for domestic semiconductor manufacturing and research, aiming to reduce dependence on Asian chipmakers.",
        "source_name": "White House",
        "source_country": "USA",
        "policy_type": "subsidy",
        "status": "enacted",
        "announced_date": "2022-08-09",
        "effective_date": "2022-08-09",
        "affected_sectors": ["Semiconductors", "Technology"],
        "sentiment_score": 0.60,
        "impact_severity": "critical",
    },
    {
        "title": "China Restricts Gallium and Germanium Exports",
        "summary": "China implements export controls on gallium and germanium, critical materials for semiconductor manufacturing, affecting global chip supply chains.",
        "source_name": "Ministry of Commerce China",
        "source_country": "CHN",
        "policy_type": "export_restriction",
        "status": "enacted",
        "announced_date": "2023-07-03",
        "effective_date": "2023-08-01",
        "affected_sectors": ["Semiconductors", "Defense", "Telecommunications"],
        "sentiment_score": -0.80,
        "impact_severity": "high",
    },
    {
        "title": "EU Carbon Border Adjustment Mechanism (CBAM) Implementation",
        "summary": "EU's carbon border tax on imports from high-emission countries takes effect, affecting steel, cement, aluminum, fertilizers and electricity imports.",
        "source_name": "EU Commission",
        "source_country": "EUR",
        "policy_type": "regulation",
        "status": "enacted",
        "announced_date": "2023-10-01",
        "effective_date": "2026-01-01",
        "affected_sectors": ["Materials", "Industrials", "Energy"],
        "sentiment_score": -0.35,
        "impact_severity": "medium",
    },
    {
        "title": "India Production Linked Incentive for Electronics Manufacturing",
        "summary": "India's PLI scheme offers 4-6% incentive on incremental sales for mobile phone and electronic components manufacturing, attracting Apple, Samsung supply chain shifts.",
        "source_name": "PIB India",
        "source_country": "IND",
        "policy_type": "subsidy",
        "status": "enacted",
        "announced_date": "2020-04-01",
        "effective_date": "2020-08-01",
        "affected_sectors": ["Technology", "Consumer Electronics"],
        "sentiment_score": 0.70,
        "impact_severity": "high",
    },
]


async def seed():
    print("Connecting to database...")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    # Import models
    from app.models.company import Company
    from app.models.policy import GovernmentPolicy
    from app.models.risk import SupplyChainRelationship
    from app.db.postgres import Base
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created")
    
    async with AsyncSessionLocal() as session:
        # Seed companies
        company_map = {}  # ticker -> UUID
        companies_added = 0
        
        for c_data in COMPANIES:
            from sqlalchemy import select, func
            result = await session.execute(
                select(Company).where(func.upper(Company.ticker) == c_data["ticker"].upper())
            )
            existing = result.scalar_one_or_none()
            if not existing:
                company = Company(**c_data)
                session.add(company)
                await session.flush()
                company_map[c_data["ticker"]] = company.id
                companies_added += 1
            else:
                company_map[c_data["ticker"]] = existing.id
        
        await session.commit()
        print(f"Companies: {companies_added} added, {len(COMPANIES) - companies_added} already existed")
        
        # Seed supply chain relationships
        rels_added = 0
        for rel in SUPPLY_CHAIN_RELATIONSHIPS:
            supplier_id = company_map.get(rel["supplier"])
            buyer_id = company_map.get(rel["buyer"])
            if supplier_id and buyer_id:
                sc_rel = SupplyChainRelationship(
                    supplier_id=supplier_id,
                    buyer_id=buyer_id,
                    product=rel["product"],
                    share_of_cogs=rel["share_of_cogs"],
                    contract_type=rel["contract_type"],
                    confidence=rel["confidence"],
                    source=rel["source"],
                )
                session.add(sc_rel)
                rels_added += 1
        
        await session.commit()
        print(f"Supply chain relationships: {rels_added} added")
        
        # Seed policies
        policies_added = 0
        for p_data in SEED_POLICIES:
            policy = GovernmentPolicy(**p_data)
            session.add(policy)
            policies_added += 1
        
        await session.commit()
        print(f"Policies: {policies_added} added")
    
    await engine.dispose()
    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
