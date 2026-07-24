# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.core.schemas import KeelSchemas


class ItemSerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    name: str
    content: str | None = None
    description: str | None = None
    is_active: bool | None = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ItemCreateSerializers(KeelSchemas):
    name: str
    content: str | None = None
    description: str | None = ""
    is_active: bool = True


class ItemUpdateSerializers(KeelSchemas):
    name: str | None = None
    content: str | None = None
    description: str | None = None
    is_active: bool | None = None
