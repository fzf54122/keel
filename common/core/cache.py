# -*- coding: utf-8 -*-
"""Redis cache manager."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import redis.asyncio as redis

from common.logger import logger
from conf import settings


class CacheManager:
    def __init__(self) -> None:
        self.redis: redis.Redis | None = None
        self._lock = asyncio.Lock()

    async def connect(self):
        if self.redis:
            return self.redis
        async with self._lock:
            if self.redis:
                return self.redis
            try:
                self.redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    socket_timeout=3,
                    socket_connect_timeout=3,
                    retry_on_timeout=False,
                    protocol=2,
                )
                await asyncio.wait_for(self.redis.ping(), timeout=3)
                logger.info("Redis connected")
            except Exception as e:
                logger.warning(f"Redis unavailable: {e}")
                self.redis = None
        return self.redis

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            logger.info("Redis disconnected")

    async def get(self, key: str) -> Any | None:
        if not self.redis:
            return None
        try:
            data = await asyncio.wait_for(self.redis.get(key), timeout=2)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get failed key={key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self.redis:
            return False
        try:
            ttl = ttl or settings.CACHE_TTL
            data = json.dumps(value, ensure_ascii=False, default=str)
            await asyncio.wait_for(self.redis.setex(key, ttl, data), timeout=2)
            return True
        except Exception as e:
            logger.error(f"Redis set failed key={key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.redis:
            return False
        try:
            await asyncio.wait_for(self.redis.delete(key), timeout=2)
            return True
        except Exception as e:
            logger.error(f"Redis delete failed key={key}: {e}")
            return False


cache_manager = CacheManager()
