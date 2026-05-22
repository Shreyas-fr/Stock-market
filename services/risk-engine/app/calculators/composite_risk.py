from typing import Dict, Optional
from loguru import logger
from .supply_chain_risk import SupplyChainRiskCalculator
from .financial_risk import FinancialRiskCalculator
from .geopolitical_risk import GeopoliticalRiskCalculator


class CompositeRiskCalculator:
    """
    Composite risk score = weighted sum of component scores.
    Overall: 0.0 (no risk) to 1.0 (extreme risk)
    """

    WEIGHTS = {
        "supply_chain": 0.30,
        "financial": 0.25,
        "geopolitical": 0.20,
        "regulatory": 0.15,
        "market": 0.10,
    }

    def __init__(self):
        self.sc_calc = SupplyChainRiskCalculator()
        self.fin_calc = FinancialRiskCalculator()
        self.geo_calc = GeopoliticalRiskCalculator()

    async def calculate(self, company_id: str) -> Dict:
        try:
            sc_risk = await self.sc_calc.calculate(company_id)
            fin_risk = await self.fin_calc.calculate(company_id)
            geo_risk = await self.geo_calc.calculate(company_id)

            # Regulatory and market risk use heuristic defaults for now
            reg_risk = 0.4
            mkt_risk = 0.35

            components = {
                "supply_chain": sc_risk,
                "financial": fin_risk,
                "geopolitical": geo_risk,
                "regulatory": reg_risk,
                "market": mkt_risk,
            }

            overall = sum(self.WEIGHTS[k] * v for k, v in components.items())
            overall = round(min(max(overall, 0.0), 1.0), 4)

            # Risk level label
            if overall >= 0.7:
                risk_level = "critical"
            elif overall >= 0.5:
                risk_level = "high"
            elif overall >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"

            return {
                "company_id": company_id,
                "overall_risk": overall,
                "risk_level": risk_level,
                "components": components,
                "weights": self.WEIGHTS,
                "model_version": "1.0.0",
            }

        except Exception as e:
            logger.error(f"Risk calculation failed for {company_id}: {e}")
            return {
                "company_id": company_id,
                "overall_risk": 0.5,
                "risk_level": "unknown",
                "error": str(e),
            }
