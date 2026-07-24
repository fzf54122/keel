# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class ApiModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}api"

    path: Mapped[str] = mapped_column(String(200), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), default="")
    tags: Mapped[str] = mapped_column(String(100), default="")
