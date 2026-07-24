# -*- coding: utf-8 -*-
from __future__ import annotations

from fast_generic_api.core.filter import FilterSet

from application.modules.demo.models import ItemModel


class ItemFilter(FilterSet):
    """Demo 过滤：?name__icontains=xx&is_active=true"""

    model = ItemModel
    name__icontains: str | None = None
    is_active: bool | None = None
