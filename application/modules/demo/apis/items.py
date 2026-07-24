# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter
from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.modules.demo.models import ItemModel
from application.modules.demo.serializers import (
    ItemCreateSerializers,
    ItemSerializers,
    ItemUpdateSerializers,
)
from application.db.backend import backend_provider
from application.pagination import LimitOffsetMaxDefaultPagination
from common.core.permission import DependPermisson
from conf import settings

router = APIRouter(tags=["Demo Items"])


class ItemViewSet(CustomViewSet, GenericAPIView):
    router = router
    prefix = "/items"
    queryset = ItemModel
    ordering = ["-created_at"]
    loop_uuid_field = "uuid"
    lookup_field = "uuid"
    search_fields = ["name", "content"]
    serializer_class = ItemSerializers
    serializer_create_class = ItemCreateSerializers
    serializer_update_class = ItemUpdateSerializers
    pagination_class = LimitOffsetMaxDefaultPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]
