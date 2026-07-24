# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.modules.rbac.models.associations import user_role_table
from application.db.base import KeelModel
from conf import settings

if TYPE_CHECKING:
    from application.modules.rbac.models.role import RoleModel


class UserModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}user"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    alias: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    roles: Mapped[list["RoleModel"]] = relationship(
        secondary=user_role_table,
        lazy="selectin",
    )
