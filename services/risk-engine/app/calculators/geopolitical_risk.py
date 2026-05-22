from loguru import logger
from typing import Dict

# Country risk scores (0.0 = stable, 1.0 = very high risk)
# Based on: political stability, sanctions exposure, trade disputes
COUNTRY_RISK_SCORES: Dict[str, float] = {
    "USA": 0.15,
    "GBR": 0.15,
    "DEU": 0.15,
    "JPN": 0.15,
    "KOR": 0.20,
    "SGP": 0.15,
    "AUS": 0.15,
    "IND": 0.30,
    "CHN": 0.55,
    "TWN": 0.50,
    "RUS": 0.90,
    "IRN": 0.95,
    "MYS": 0.30,
    "VNM": 0.35,
    "THA": 0.30,
    "IDN": 0.35,
    "PHL": 0.35,
    "MEX": 0.40,
    "BRA": 0.40,
    "ZAF": 0.45,
    "NGA": 0.70,
    "COD": 0.75,  # DRC - critical minerals
    "COG": 0.65,  # Congo
    "CHL": 0.30,  # lithium
    "ARG": 0.50,  # lithium
    "BOL": 0.55,  # lithium
}


class GeopoliticalRiskCalculator:
    """
    Geopolitical risk based on:
    - Supplier country political stability
    - Sanctions exposure
    - Trade war signals
    - Export control risks
    """

    async def calculate(self, company_id: str) -> float:
        try:
            score = await self._calculate_geo_exposure(company_id)
            return round(min(max(score, 0.0), 1.0), 4)
        except Exception as e:
            logger.warning(f"Geo risk fallback for {company_id}: {e}")
            return 0.35

    async def _calculate_geo_exposure(self, company_id: str) -> float:
        """
        Real implementation: query Neo4j to get supplier countries,
        then compute weighted average of country risk scores.
        """
        # Placeholder: return moderate score
        return 0.35

    def country_risk(self, country_code: str) -> float:
        return COUNTRY_RISK_SCORES.get(country_code.upper(), 0.50)
