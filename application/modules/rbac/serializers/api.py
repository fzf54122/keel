# -*- coding: utf-8 -*-
from __future__ import annotations

from uuid import UUID

from common.core.schemas import KeelSchemas


class APISerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    path: str | None = None
    method: str | None = None
    summary: str | None = None
    tags: str | None = None
    is_active: bool | None = True


class APICreateSerializers(KeelSchemas):
    path: str
    method: str
    summary: str = ""
    tags: str = ""


class APIUpdateSerializers(APICreateSerializers):
    pass
