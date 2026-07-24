# -*- coding: utf-8 -*-
"""Schema 基类（脚手架规范）。"""

from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class KeelSchemas(BaseModel):
    model_config = {"from_attributes": True}

    @property
    def data(self) -> Any:
        return jsonable_encoder(self)
