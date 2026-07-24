# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class ItemModel(KeelModel):
    """Minimal demo resource for verifying the scaffold."""

    __tablename__ = f"{settings.TABLE_PREFIX}item"

    name: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
