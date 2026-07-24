# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter
from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.modules.rbac.models import DeptsModel
from application.modules.rbac.serializers import (
    DeptCreateSerializers,
    DeptSerializers,
    DeptUpdateSerializers,
)
from application.db.backend import backend_provider
from application.pagination import LimitOffsetMaxDefaultPagination
from common.core.permission import DependPermisson
from conf import settings

router = APIRouter(tags=["部门管理"])


class DeptViewSet(CustomViewSet, GenericAPIView):
    router = router
    prefix = "/depts"
    queryset = DeptsModel
    ordering = ["order", "id"]
    loop_uuid_field = "uuid"
    lookup_field = "uuid"
    serializer_class = DeptSerializers
    serializer_create_class = DeptCreateSerializers
    serializer_update_class = DeptUpdateSerializers
    pagination_class = LimitOffsetMaxDefaultPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]
