# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.core.schemas import KeelSchemas
from pydantic import Field


class RoleSerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    name: str | None = None
    desc: str | None = ""
    is_active: bool = True
    menus: list | None = None
    apis: list | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RoleCreateSerializers(KeelSchemas):
    name: str = Field(..., description="角色名称")
    desc: str = Field("", description="角色描述")
    is_active: bool = True
    menu_ids: list[int] = []
    api_ids: list[int] = []


class RoleUpdateSerializers(RoleCreateSerializers):
    pass
