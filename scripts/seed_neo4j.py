#!/usr/bin/env python3
"""
Seed Neo4j graph with companies and supply chain relationships.
Run: python scripts/seed_neo4j.py
"""

import asyncio
import os
from neo4j import AsyncGraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "sci_password")

NODES = [
    # Sectors
    {"type": "Sector", "data": {"id": "s_technology", "name": "Technology", "gics": "45"}},
    {"type": "Sector", "data": {"id": "s_ev", "name": "Electric Vehicles", "gics": "2510"}},
    {"type": "Sector", "data": {"id": "s_semiconductors", "name": "Semiconductors", "gics": "4530"}},
    {"type": "Sector", "data": {"id": "s_battery", "name": "Battery Manufacturing", "gics": "2010"}},
    {"type": "Sector", "data": {"id": "s_industrials", "name": "Industrials", "gics": "20"}},
    {"type": "Sector", "data": {"id": "s_energy", "name": "Energy", "gics": "10"}},
    {"type": "Sector", "data": {"id": "s_healthcare", "name": "Healthcare", "gics": "35"}},
    {"type": "Sector", "data": {"id": "s_materials", "name": "Materials", "gics": "15"}},
    
    # Countries
    {"type": "Country", "data": {"code": "USA", "name": "United States", "region": "North America"}},
    {"type": "Country", "data": {"code": "CHN", "name": "China", "region": "Asia"}},
    {"type": "Country", "data": {"code": "TWN", "name": "Taiwan", "region": "Asia"}},
    {"type": "Country", "data": {"code": "KOR", "name": "South Korea", "region": "Asia"}},
    {"type": "Country", "data": {"code": "JPN", "name": "Japan", "region": "Asia"}},
    {"type": "Country", "data": {"code": "IND", "name": "India", "region": "South Asia"}},
    {"type": "Country", "data": {"code": "DEU", "name": "Germany", "region": "Europe"}},
    
    # Companies  
    {"type": "Company", "data": {"id": "c_aapl", "ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "country": "USA", "riskScore": 0.35, "marketCap": 2900000000000}},
    {"type": "Company", "data": {"id": "c_tsm", "ticker": "TSM", "name": "TSMC", "sector": "Semiconductors", "country": "TWN", "riskScore": 0.58, "marketCap": 550000000000}},
    {"type": "Company", "data": {"id": "c_nvda", "ticker": "NVDA", "name": "NVIDIA", "sector": "Semiconductors", "country": "USA", "riskScore": 0.42, "marketCap": 2500000000000}},
    {"type": "Company", "data": {"id": "c_tsla", "ticker": "TSLA", "name": "Tesla Inc.", "sector": "Electric Vehicles", "country": "USA", "riskScore": 0.55, "marketCap": 700000000000}},
    {"type": "Company", "data": {"id": "c_lges", "ticker": "LGES.KS", "name": "LG Energy Solution", "sector": "Battery Manufacturing", "country": "KOR", "riskScore": 0.40, "marketCap": 70000000000}},
    {"type": "Company", "data": {"id": "c_pcrfy", "ticker": "PCRFY", "name": "Panasonic", "sector": "Battery Manufacturing", "country": "JPN", "riskScore": 0.38, "marketCap": 25000000000}},
    {"type": "Company", "data": {"id": "c_alb", "ticker": "ALB", "name": "Albemarle", "sector": "Materials", "country": "USA", "riskScore": 0.60, "marketCap": 10000000000}},
    {"type": "Company", "data": {"id": "c_qcom", "ticker": "QCOM", "name": "Qualcomm", "sector": "Semiconductors", "country": "USA", "riskScore": 0.40, "marketCap": 200000000000}},
    {"type": "Company", "data": {"id": "c_sony", "ticker": "SONY", "name": "Sony", "sector": "Technology", "country": "JPN", "riskScore": 0.38, "marketCap": 120000000000}},
    {"type": "Company", "data": {"id": "c_amat", "ticker": "AMAT", "name": "Applied Materials", "sector": "Semiconductors", "country": "USA", "riskScore": 0.45, "marketCap": 150000000000}},
    {"type": "Company", "data": {"id": "c_intc", "ticker": "INTC", "name": "Intel", "sector": "Semiconductors", "country": "USA", "riskScore": 0.52, "marketCap": 100000000000}},
    {"type": "Company", "data": {"id": "c_tatam", "ticker": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Electric Vehicles", "country": "IND", "riskScore": 0.48, "marketCap": 28000000000}},
    {"type": "Company", "data": {"id": "c_samsung", "ticker": "SNE", "name": "Samsung Electronics", "sector": "Technology", "country": "KOR", "riskScore": 0.42, "marketCap": 330000000000}},
]

RELATIONSHIPS = [
    # SUPPLIES
    {"from": "c_tsm", "to": "c_aapl", "type": "SUPPLIES", "props": {"product": "A-series chips", "shareOfCOGS": 0.18, "contractType": "sole-source", "confidence": 0.95}},
    {"from": "c_qcom", "to": "c_aapl", "type": "SUPPLIES", "props": {"product": "5G modems", "shareOfCOGS": 0.05, "contractType": "multi-source", "confidence": 0.90}},
    {"from": "c_sony", "to": "c_aapl", "type": "SUPPLIES", "props": {"product": "CMOS sensors", "shareOfCOGS": 0.04, "contractType": "sole-source", "confidence": 0.88}},
    {"from": "c_samsung", "to": "c_aapl", "type": "SUPPLIES", "props": {"product": "OLED displays", "shareOfCOGS": 0.08, "contractType": "multi-source", "confidence": 0.85}},
    {"from": "c_tsm", "to": "c_nvda", "type": "SUPPLIES", "props": {"product": "GPU wafers", "shareOfCOGS": 0.55, "contractType": "sole-source", "confidence": 0.98}},
    {"from": "c_pcrfy", "to": "c_tsla", "type": "SUPPLIES", "props": {"product": "cylindrical cells", "shareOfCOGS": 0.22, "contractType": "multi-source", "confidence": 0.92}},
    {"from": "c_lges", "to": "c_tsla", "type": "SUPPLIES", "props": {"product": "NMC battery cells", "shareOfCOGS": 0.15, "contractType": "multi-source", "confidence": 0.90}},
    {"from": "c_alb", "to": "c_lges", "type": "SUPPLIES", "props": {"product": "lithium hydroxide", "shareOfCOGS": 0.25, "contractType": "multi-source", "confidence": 0.88}},
    {"from": "c_alb", "to": "c_pcrfy", "type": "SUPPLIES", "props": {"product": "lithium carbonate", "shareOfCOGS": 0.20, "contractType": "multi-source", "confidence": 0.85}},
    {"from": "c_alb", "to": "c_tsla", "type": "SUPPLIES", "props": {"product": "lithium hydroxide direct", "shareOfCOGS": 0.06, "contractType": "multi-source", "confidence": 0.88}},
    {"from": "c_amat", "to": "c_tsm", "type": "SUPPLIES", "props": {"product": "fab equipment", "shareOfCOGS": 0.15, "contractType": "multi-source", "confidence": 0.90}},
    {"from": "c_amat", "to": "c_intc", "type": "SUPPLIES", "props": {"product": "fab equipment", "shareOfCOGS": 0.12, "contractType": "multi-source", "confidence": 0.82}},
    {"from": "c_lges", "to": "c_tatam", "type": "SUPPLIES", "props": {"product": "EV battery packs", "shareOfCOGS": 0.28, "contractType": "multi-source", "confidence": 0.85}},
    
    # BELONGS_TO
    {"from": "c_aapl", "to": "s_technology", "type": "BELONGS_TO", "props": {}},
    {"from": "c_nvda", "to": "s_semiconductors", "type": "BELONGS_TO", "props": {}},
    {"from": "c_tsm", "to": "s_semiconductors", "type": "BELONGS_TO", "props": {}},
    {"from": "c_tsla", "to": "s_ev", "type": "BELONGS_TO", "props": {}},
    {"from": "c_lges", "to": "s_battery", "type": "BELONGS_TO", "props": {}},
    {"from": "c_pcrfy", "to": "s_battery", "type": "BELONGS_TO", "props": {}},
    {"from": "c_alb", "to": "s_materials", "type": "BELONGS_TO", "props": {}},
    {"from": "c_intc", "to": "s_semiconductors", "type": "BELONGS_TO", "props": {}},
    {"from": "c_tatam", "to": "s_ev", "type": "BELONGS_TO", "props": {}},
    {"from": "c_samsung", "to": "s_technology", "type": "BELONGS_TO", "props": {}},
    
    # HEADQUARTERED_IN
    {"from": "c_aapl", "to": "USA", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_tsm", "to": "TWN", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_nvda", "to": "USA", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_tsla", "to": "USA", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_lges", "to": "KOR", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_pcrfy", "to": "JPN", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_sony", "to": "JPN", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_alb", "to": "USA", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_tatam", "to": "IND", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
    {"from": "c_samsung", "to": "KOR", "type": "HEADQUARTERED_IN", "props": {}, "to_label": "Country"},
]


async def seed_neo4j():
    print(f"Connecting to Neo4j at {NEO4J_URI}...")
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    async with driver.session() as session:
        # Clear existing data
        await session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing Neo4j data")
        
        # Create constraints
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.ticker IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sector) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Country) REQUIRE c.code IS UNIQUE",
        ]
        for c in constraints:
            try:
                await session.run(c)
            except Exception as e:
                print(f"Constraint warning: {e}")
        
        # Create nodes
        nodes_created = 0
        for node in NODES:
            label = node["type"]
            data = node["data"]
            props = ", ".join(f"{k}: ${k}" for k in data.keys())
            query = f"MERGE (n:{label} {{{props}}}) SET n += ${{'props': $props}}"
            # Simpler approach:
            set_clause = ", ".join(f"n.{k} = ${k}" for k in data.keys())
            if label == "Country":
                await session.run(
                    f"MERGE (n:Country {{code: $code}}) SET {set_clause}",
                    **data
                )
            elif label == "Sector":
                await session.run(
                    f"MERGE (n:Sector {{id: $id}}) SET {set_clause}",
                    **data
                )
            elif label == "Company":
                await session.run(
                    f"MERGE (n:Company {{id: $id}}) SET {set_clause}",
                    **data
                )
            nodes_created += 1
        
        print(f"Created {nodes_created} nodes")
        
        # Create relationships
        rels_created = 0
        for rel in RELATIONSHIPS:
            to_label = rel.get("to_label", "")
            props = rel.get("props", {})
            
            if rel["type"] == "SUPPLIES":
                cypher = """
                MATCH (a:Company {id: $from_id}), (b:Company {id: $to_id})
                MERGE (a)-[r:SUPPLIES]->(b)
                SET r += $props
                """
                await session.run(cypher, from_id=rel["from"], to_id=rel["to"], props=props)
            
            elif rel["type"] == "BELONGS_TO":
                cypher = """
                MATCH (a:Company {id: $from_id}), (b:Sector {id: $to_id})
                MERGE (a)-[:BELONGS_TO]->(b)
                """
                await session.run(cypher, from_id=rel["from"], to_id=rel["to"])
            
            elif rel["type"] == "HEADQUARTERED_IN":
                cypher = """
                MATCH (a:Company {id: $from_id}), (b:Country {code: $to_id})
                MERGE (a)-[:HEADQUARTERED_IN]->(b)
                """
                await session.run(cypher, from_id=rel["from"], to_id=rel["to"])
            
            rels_created += 1
        
        print(f"Created {rels_created} relationships")
    
    await driver.close()
    print("\n✅ Neo4j seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_neo4j())
