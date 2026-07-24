# -*- coding: utf-8 -*-
"""后台任务上下文（脚手架规范）。"""

from __future__ import annotations

import contextvars

from starlette.background import BackgroundTasks

CTX_USER_ID: contextvars.ContextVar[int] = contextvars.ContextVar("user_id", default=0)
CTX_BG_TASKS: contextvars.ContextVar[BackgroundTasks | None] = contextvars.ContextVar(
    "bg_task", default=None
)


class KeelTask:
    @classmethod
    async def init_bg_tasks_obj(cls) -> None:
        CTX_BG_TASKS.set(BackgroundTasks())

    @classmethod
    async def get_bg_tasks_obj(cls) -> BackgroundTasks | None:
        return CTX_BG_TASKS.get()

    @classmethod
    async def add_task(cls, func, *args, **kwargs) -> None:
        bg_tasks = await cls.get_bg_tasks_obj()
        if bg_tasks is not None:
            bg_tasks.add_task(func, *args, **kwargs)

    @classmethod
    async def execute_tasks(cls) -> None:
        bg_tasks = await cls.get_bg_tasks_obj()
        if bg_tasks and bg_tasks.tasks:
            await bg_tasks()
