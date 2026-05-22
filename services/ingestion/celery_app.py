from celery import Celery
from celery.schedules import crontab
import os

broker_url = os.getenv("CELERY_BROKER_URL", "redis://:sci_password@localhost:6379/1")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://:sci_password@localhost:6379/2")

app = Celery(
    "sci_ingestion",
    broker=broker_url,
    backend=result_backend,
    include=[
        "tasks.price_tasks",
        "tasks.news_tasks",
        "tasks.policy_tasks",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

app.conf.beat_schedule = {
    # Update stock prices every 5 minutes during market hours
    "update-stock-prices": {
        "task": "tasks.price_tasks.update_all_prices",
        "schedule": crontab(minute="*/5"),
    },
    # Fetch news every 10 minutes
    "fetch-news": {
        "task": "tasks.news_tasks.fetch_latest_news",
        "schedule": crontab(minute="*/10"),
    },
    # Check policies every 30 minutes
    "check-policies": {
        "task": "tasks.policy_tasks.check_new_policies",
        "schedule": crontab(minute="*/30"),
    },
    # Daily financial data refresh at 6 AM UTC
    "daily-financials": {
        "task": "tasks.price_tasks.update_financial_statements",
        "schedule": crontab(hour=6, minute=0),
    },
}
