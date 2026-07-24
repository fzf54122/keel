# -*- coding: utf-8 -*-
from __future__ import annotations

from uuid import UUID

from application.modules.rbac.enums import MenuType
from common.core.schemas import KeelSchemas
from pydantic import Field


class MenuSerializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    name: str | None = None
    path: str | None = None
    remark: dict | None = None
    menu_type: MenuType | str | None = None
    icon: str | None = None
    order: int | None = 0
    parent_id: int | None = 0
    is_hidden: bool | None = False
    component: str | None = None
    keepalive: bool | None = False
    redirect: str | None = None
    is_active: bool | None = True


class MenuCreateSerializers(KeelSchemas):
    menu_type: MenuType | str = Field(default=MenuType.CATALOG.value)
    name: str
    icon: str | None = None
    path: str | None = None
    order: int | None = 0
    parent_id: int | None = 0
    is_hidden: bool | None = False
    component: str | None = "Layout"
    keepalive: bool | None = True
    redirect: str | None = ""


class MenuUpdateSerializers(MenuCreateSerializers):
    pass
