# -*- coding: utf-8 -*-
"""Service 基类（脚手架规范）。"""

from __future__ import annotations

from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")


class KeelService(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model
