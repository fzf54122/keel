# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class DeptsModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}depts"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    parent_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
