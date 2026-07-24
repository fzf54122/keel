# -*- coding: utf-8 -*-
"""Demo async tasks."""

from __future__ import annotations

import time

from application.celery_app import celery
from common.logger import logger


@celery.task(bind=True, name="jobs.demo.add")
def add(self, x: int, y: int) -> dict:
    logger.info(f"jobs.demo.add {x}+{y} task_id={self.request.id}")
    return {"result": x + y, "task_id": self.request.id}


@celery.task(bind=True, name="jobs.demo.long_running")
def long_running(self, seconds: int = 3) -> dict:
    """可观察进度的长任务示例。"""
    seconds = max(1, min(int(seconds), 30))
    for i in range(seconds):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={"current": i + 1, "total": seconds},
        )
    return {"done": True, "seconds": seconds, "task_id": self.request.id}
