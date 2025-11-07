from core.logger.logger import LOG
from config import CONFIG
from celery import Celery


celery_app = Celery(
    "hubspot_agent",
    broker=CONFIG.celery_broker_url,
    backend=CONFIG.celery_result_backend,
    include=["modules.celery.tasks"]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)