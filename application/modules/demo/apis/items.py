# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.demo.models import ItemModel
from application.modules.demo.serializers import (
    ItemCreateSerializers,
    ItemSerializers,
    ItemUpdateSerializers,
)
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["Demo Items"])


class ItemViewSet(KeelViewSet):
    router = router
    prefix = "/items"
    queryset = ItemModel
    search_fields = ["name", "content"]
    serializer_class = ItemSerializers
    serializer_create_class = ItemCreateSerializers
    serializer_update_class = ItemUpdateSerializers
