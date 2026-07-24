# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter
from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.modules.rbac.models import MenuModel
from application.modules.rbac.serializers import (
    MenuCreateSerializers,
    MenuSerializers,
    MenuUpdateSerializers,
)
from application.db.backend import backend_provider
from application.pagination import LimitOffsetMaxDefaultPagination
from common.core.permission import DependPermisson
from conf import settings

router = APIRouter(tags=["菜单管理"])


class MenuViewSet(CustomViewSet, GenericAPIView):
    router = router
    prefix = "/menus"
    queryset = MenuModel
    ordering = ["order", "id"]
    loop_uuid_field = "uuid"
    lookup_field = "uuid"
    serializer_class = MenuSerializers
    serializer_create_class = MenuCreateSerializers
    serializer_update_class = MenuUpdateSerializers
    pagination_class = LimitOffsetMaxDefaultPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]
