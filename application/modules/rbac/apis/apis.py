# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Request
from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.modules.rbac.models import ApiModel
from application.modules.rbac.serializers import (
    APICreateSerializers,
    APISerializers,
    APIUpdateSerializers,
)
from application.modules.rbac.services import ApiService
from application.db.backend import backend_provider
from application.pagination import LimitOffsetMaxDefaultPagination
from common.core.permission import DependPermisson
from common.core.response import KeelResponse
from conf import settings

router = APIRouter(tags=["API管理"])
service = ApiService()


class ApiViewSet(CustomViewSet, GenericAPIView):
    router = router
    prefix = "/apis"
    queryset = ApiModel
    ordering = ["id"]
    loop_uuid_field = "uuid"
    lookup_field = "uuid"
    serializer_class = APISerializers
    serializer_create_class = APICreateSerializers
    serializer_update_class = APIUpdateSerializers
    pagination_class = LimitOffsetMaxDefaultPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]

    @staticmethod
    @router.post("/refresh/", summary="同步路由到API表")
    async def refresh(request: Request):
        await service.refresh_api(request.app)
        return KeelResponse(msg="API 同步完成")
