from typing import Dict
from loguru import logger


class SupplyChainRiskCalculator:
    """
    Supply chain risk factors:
    - Geographic concentration (HHI index)
    - Single-source dependencies
    - Supplier count & diversity
    - Disruption signals from news/policies
    """

    async def calculate(self, company_id: str) -> float:
        try:
            # In production: query Neo4j for supply chain topology
            # and PostgreSQL for recent disruption events
            score = await self._calculate_from_graph(company_id)
            return round(min(max(score, 0.0), 1.0), 4)
        except Exception as e:
            logger.warning(f"SC risk fallback for {company_id}: {e}")
            return 0.45  # neutral fallback

    async def _calculate_from_graph(self, company_id: str) -> float:
        """
        HHI-based geographic concentration risk.
        
        HHI = sum of squared market shares per country
        HHI = 1.0 (monopoly) -> high risk
        HHI near 0 -> low risk
        """
        # Placeholder implementation
        # Real: query Neo4j MATCH (c)<-[:SUPPLIES*1..2]-(s)-[:HEADQUARTERED_IN]->(country)
        
        # Simulated: return moderate risk
        geo_concentration = 0.4  # Would come from Neo4j query
        single_source_penalty = 0.1
        
        return geo_concentration + single_source_penalty

    def _hhi(self, shares: list) -> float:
        """Herfindahl-Hirschman Index."""
        if not shares:
            return 0.0
        total = sum(shares)
        if total == 0:
            return 0.0
        normalized = [s / total for s in shares]
        return sum(s ** 2 for s in normalized)
