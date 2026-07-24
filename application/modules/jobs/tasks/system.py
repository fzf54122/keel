# -*- coding: utf-8 -*-
"""System maintenance tasks (beat)."""

from __future__ import annotations

from datetime import datetime

from application.celery_app import celery
from common.logger import logger


@celery.task(name="jobs.system.heartbeat")
def heartbeat() -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    from conf import settings

    logger.info(f"{settings.PROJECT_NAME} heartbeat at {now}")
    return {"ok": True, "at": now}


@celery.task(name="jobs.system.daily_cleanup")
def daily_cleanup() -> dict:
    """占位清理任务：业务可替换为真实清理逻辑。"""
    logger.info("daily_cleanup placeholder executed")
    return {"ok": True, "action": "cleanup-placeholder"}
