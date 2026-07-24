# -*- coding: utf-8 -*-
"""Celery application entry.

Start worker / beat::

    celery -A application.celery_app.celery worker -l info
    celery -A application.celery_app.celery beat -l info
"""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from conf import settings

celery = Celery(
    settings.PROJECT_NAME,
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=[
        "application.modules.jobs.tasks.demo",
        "application.modules.jobs.tasks.system",
    ],
)

celery.conf.update(
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=False,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=60 * 60 * 24,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
    task_store_eager_result=True,
    beat_schedule={
        # 每分钟心跳，验证 beat 可用
        f"{settings.PROJECT_NAME}-heartbeat-every-minute": {
            "task": "jobs.system.heartbeat",
            "schedule": 60.0,
        },
        # 每天 03:15 清理示例（占位）
        f"{settings.PROJECT_NAME}-daily-cleanup": {
            "task": "jobs.system.daily_cleanup",
            "schedule": crontab(hour=3, minute=15),
        },
    },
)


@celery.task(bind=True, name="jobs.ping")
def ping(self, message: str = "pong") -> dict:
    return {"ok": True, "message": message, "task_id": self.request.id}
