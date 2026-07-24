# -*- coding: utf-8 -*-
from __future__ import annotations

from uuid import UUID

from common.core.schemas import KeelSchemas
from pydantic import Field


class DeptSerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    name: str | None = None
    desc: str | None = None
    order: int | None = 0
    parent_id: int | None = 0
    is_active: bool | None = True


class DeptCreateSerializers(KeelSchemas):
    name: str = Field(..., description="部门名称")
    desc: str | None = None
    order: int = 0
    parent_id: int = 0


class DeptUpdateSerializers(DeptCreateSerializers):
    pass
