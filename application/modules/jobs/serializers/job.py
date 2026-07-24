# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

from common.core.schemas import KeelSchemas
from pydantic import Field


class JobEnqueueSerializers(KeelSchemas):
    x: int = Field(1, description="加数 x")
    y: int = Field(2, description="加数 y")


class LongRunningSerializers(KeelSchemas):
    seconds: int = Field(3, ge=1, le=30, description="模拟耗时秒数")


class JobStatusSerializers(KeelSchemas):
    task_id: str
    state: str
    result: Any = None
    info: Any = None
