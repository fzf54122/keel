# -*- coding: utf-8 -*-
"""Many-to-many association tables."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Table

from application.db.base import Base
from conf import settings

prefix = settings.TABLE_PREFIX

role_menu_table = Table(
    f"{prefix}role_menu",
    Base.metadata,
    Column("role_id", Integer, ForeignKey(f"{prefix}role.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_id", Integer, ForeignKey(f"{prefix}menu.id", ondelete="CASCADE"), primary_key=True),
)

role_api_table = Table(
    f"{prefix}role_api",
    Base.metadata,
    Column("role_id", Integer, ForeignKey(f"{prefix}role.id", ondelete="CASCADE"), primary_key=True),
    Column("api_id", Integer, ForeignKey(f"{prefix}api.id", ondelete="CASCADE"), primary_key=True),
)

user_role_table = Table(
    f"{prefix}user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey(f"{prefix}user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey(f"{prefix}role.id", ondelete="CASCADE"), primary_key=True),
)
