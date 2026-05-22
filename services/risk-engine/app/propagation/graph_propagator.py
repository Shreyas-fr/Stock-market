from typing import Dict, List
from loguru import logger
from collections import deque


class GraphPropagator:
    """
    BFS-based impact propagation through supply chain graph.
    
    Algorithm:
    1. Start with directly-affected companies (Tier 0)
    2. Find their suppliers (Tier 1)
    3. Find Tier 1 suppliers' suppliers (Tier 2)
    4. Apply exponential decay: impact = base_impact * decay^tier * cogs_share
    """

    DEFAULT_DECAY = 0.5
    MAX_HOPS = 3

    async def propagate(
        self,
        policy_id: str,
        decay_factor: float = None,
        max_hops: int = None,
    ) -> Dict:
        decay_factor = decay_factor or self.DEFAULT_DECAY
        max_hops = max_hops or self.MAX_HOPS

        try:
            # Step 1: Get directly affected companies
            direct = await self._get_direct_impact(policy_id)

            # Step 2: BFS propagation
            impact_map = {c["id"]: {"score": c["impact"], "tier": 0, "path": [c["id"]]} for c in direct}
            queue = deque([(c["id"], c["impact"], 0) for c in direct])

            while queue:
                company_id, impact, hop = queue.popleft()
                if hop >= max_hops:
                    continue

                suppliers = await self._get_suppliers(company_id)
                for supplier in suppliers:
                    propagated = impact * decay_factor * supplier.get("cogs_share", 0.3)
                    existing = impact_map.get(supplier["id"], {}).get("score", 0)
                    if propagated > existing:
                        impact_map[supplier["id"]] = {
                            "score": round(propagated, 4),
                            "tier": hop + 1,
                            "path": impact_map.get(company_id, {}).get("path", []) + [supplier["id"]],
                        }
                        queue.append((supplier["id"], propagated, hop + 1))

            return {
                "policy_id": policy_id,
                "decay_factor": decay_factor,
                "max_hops": max_hops,
                "impacted_companies": len(impact_map),
                "impact_map": impact_map,
            }

        except Exception as e:
            logger.error(f"Propagation failed for policy {policy_id}: {e}")
            return {"policy_id": policy_id, "error": str(e), "impact_map": {}}

    async def _get_direct_impact(self, policy_id: str) -> List[Dict]:
        """
        In production: query Neo4j for companies directly affected by policy.
        MATCH (p:Policy {id: $pid})-[:AFFECTS_SECTOR]->(s:Sector)<-[:BELONGS_TO]-(c:Company)
        """
        # Placeholder
        return []

    async def _get_suppliers(self, company_id: str) -> List[Dict]:
        """
        In production: query Neo4j for suppliers of a company.
        MATCH (supplier:Company)-[r:SUPPLIES]->(c:Company {id: $cid})
        RETURN supplier.id, r.shareOfCOGS AS cogs_share
        """
        # Placeholder
        return []
