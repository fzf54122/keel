# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.modules.rbac.models.associations import role_api_table, role_menu_table
from application.db.base import KeelModel
from conf import settings

if TYPE_CHECKING:
    from application.modules.rbac.models.api import ApiModel
    from application.modules.rbac.models.menu import MenuModel


class RoleModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}role"

    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    desc: Mapped[str | None] = mapped_column(String(500), nullable=True)

    menus: Mapped[list["MenuModel"]] = relationship(
        secondary=role_menu_table,
        lazy="selectin",
    )
    apis: Mapped[list["ApiModel"]] = relationship(
        secondary=role_api_table,
        lazy="selectin",
    )
