# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.rbac.models import MenuModel
from application.modules.rbac.serializers import (
    MenuCreateSerializers,
    MenuSerializers,
    MenuUpdateSerializers,
)
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["菜单管理"])


class MenuViewSet(KeelViewSet):
    router = router
    prefix = "/menus"
    queryset = MenuModel
    ordering = ["order", "id"]
    serializer_class = MenuSerializers
    serializer_create_class = MenuCreateSerializers
    serializer_update_class = MenuUpdateSerializers
