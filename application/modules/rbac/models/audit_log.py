# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class AuditLogModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}audit_log"

    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    module: Mapped[str | None] = mapped_column(String(64), nullable=True)
    summary: Mapped[str | None] = mapped_column(String(128), nullable=True)
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    host: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_args: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)
