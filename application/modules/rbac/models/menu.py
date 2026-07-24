# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Boolean, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class MenuModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}menu"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    remark: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    menu_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    path: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    parent_id: Mapped[int] = mapped_column(Integer, default=0)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    component: Mapped[str | None] = mapped_column(String(100), nullable=True)
    keepalive: Mapped[bool] = mapped_column(Boolean, default=True)
    redirect: Mapped[str | None] = mapped_column(String(100), nullable=True)
