# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Request

from application.modules.rbac.models import ApiModel
from application.modules.rbac.serializers import (
    APICreateSerializers,
    APISerializers,
    APIUpdateSerializers,
)
from application.modules.rbac.services import ApiService
from common.core.response import KeelResponse
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["API管理"])
service = ApiService()


class ApiViewSet(KeelViewSet):
    router = router
    prefix = "/apis"
    queryset = ApiModel
    ordering = ["id"]
    serializer_class = APISerializers
    serializer_create_class = APICreateSerializers
    serializer_update_class = APIUpdateSerializers

    @staticmethod
    @router.post("/apis/refresh/", summary="同步路由到API表")
    async def refresh(request: Request):
        await service.refresh_api(request.app)
        return KeelResponse(msg="API 同步完成")
