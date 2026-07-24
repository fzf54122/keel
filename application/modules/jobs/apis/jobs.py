# -*- coding: utf-8 -*-
"""Job trigger / status APIs."""

from __future__ import annotations

from fastapi import APIRouter

from application.modules.jobs.serializers import (
    JobEnqueueSerializers,
    JobStatusSerializers,
    LongRunningSerializers,
)
from application.modules.jobs.services import JobService
from common.core.permission import DependPermisson
from common.core.response import KeelResponse

router = APIRouter(tags=["任务中心"], prefix="/jobs")
service = JobService()


@router.post("/add/", summary="投递加法任务", dependencies=[DependPermisson])
async def enqueue_add(body: JobEnqueueSerializers):
    task_id = service.enqueue_add(body.x, body.y)
    return KeelResponse(data={"task_id": task_id}, msg="任务已投递")


@router.post("/long-running/", summary="投递长任务", dependencies=[DependPermisson])
async def enqueue_long_running(body: LongRunningSerializers):
    task_id = service.enqueue_long_running(body.seconds)
    return KeelResponse(data={"task_id": task_id}, msg="任务已投递")


@router.get("/{task_id}/", summary="查询任务状态", dependencies=[DependPermisson])
async def job_status(task_id: str):
    data = service.get_status(task_id)
    return KeelResponse(data=JobStatusSerializers(**data))
