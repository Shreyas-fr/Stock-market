from celery_app import app
from crawlers.policy_crawler import PolicyCrawler
from loguru import logger


@app.task(bind=True, max_retries=3)
def check_new_policies(self):
    """Crawl government sources for new policies."""
    try:
        crawler = PolicyCrawler()
        policies = crawler.fetch_all()
        
        saved = 0
        for policy in policies:
            if crawler.save_policy(policy):
                saved += 1
                # Trigger AI analysis for new policies
                analyze_policy_impact.delay(str(policy.get("id", "")))
        
        logger.info(f"Found {len(policies)} policies, saved {saved} new")
        return {"status": "success", "found": len(policies), "saved": saved}
    except Exception as e:
        logger.error(f"Policy check failed: {e}")
        raise self.retry(exc=e)


@app.task(bind=True, max_retries=2)
def analyze_policy_impact(self, policy_id: str):
    """Send policy to AI service for impact analysis."""
    import httpx
    try:
        response = httpx.post(
            "http://api:8000/api/v1/ai/policy-impact",
            json={"policy_id": policy_id},
            timeout=60,
        )
        return response.json()
    except Exception as e:
        logger.error(f"Policy impact analysis failed: {e}")
        raise self.retry(exc=e)
