# -*- coding: utf-8 -*-
from __future__ import annotations

from celery.result import AsyncResult

from application.celery_app import celery
from application.modules.jobs.tasks.demo import add, long_running


class JobService:
    def enqueue_add(self, x: int, y: int) -> str:
        result = add.delay(x, y)
        return result.id

    def enqueue_long_running(self, seconds: int) -> str:
        result = long_running.delay(seconds)
        return result.id

    def get_status(self, task_id: str) -> dict:
        async_result = AsyncResult(task_id, app=celery)
        payload = {
            "task_id": task_id,
            "state": async_result.state,
            "result": None,
            "info": None,
        }
        if async_result.successful():
            payload["result"] = async_result.result
        elif async_result.failed():
            payload["info"] = str(async_result.result)
        elif async_result.state == "PROGRESS":
            payload["info"] = async_result.info
        else:
            payload["info"] = async_result.info
        return payload
