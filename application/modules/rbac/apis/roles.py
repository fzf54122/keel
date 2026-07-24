# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter
from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.modules.rbac.models import RoleModel
from application.modules.rbac.serializers import (
    RoleCreateSerializers,
    RoleSerializers,
    RoleUpdateSerializers,
)
from application.db.backend import backend_provider
from application.pagination import LimitOffsetMaxDefaultPagination
from common.core.permission import DependPermisson
from conf import settings

router = APIRouter(tags=["角色管理"])


class RoleViewSet(CustomViewSet, GenericAPIView):
    router = router
    prefix = "/roles"
    queryset = RoleModel
    ordering = ["created_at"]
    loop_uuid_field = "uuid"
    lookup_field = "uuid"
    serializer_class = RoleSerializers
    serializer_create_class = RoleCreateSerializers
    serializer_update_class = RoleUpdateSerializers
    pagination_class = LimitOffsetMaxDefaultPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]
