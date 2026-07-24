# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from common.core.schemas import KeelSchemas


class AuditLogSerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    user_id: int | None = None
    username: str | None = None
    module: str | None = None
    summary: str | None = None
    method: str | None = None
    path: str | None = None
    host: str | None = None
    status: int | None = None
    response_time: int | None = None
    request_args: dict | None = None
    response_body: Any | None = None
    created_at: datetime | None = None
