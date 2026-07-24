# -*- coding: utf-8 -*-
"""Redis cache manager with explicit degrade / fail policy."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import redis.asyncio as redis
from fastapi import HTTPException

from common.logger import logger
from conf import settings


class CacheUnavailableError(RuntimeError):
    """Raised when Redis is required but unavailable."""


class CacheManager:
    def __init__(self) -> None:
        self.redis: redis.Redis | None = None
        self._lock = asyncio.Lock()
        self._connect_attempted = False

    @property
    def available(self) -> bool:
        return self.redis is not None

    async def connect(self):
        if self.redis:
            return self.redis
        async with self._lock:
            if self.redis:
                return self.redis
            self._connect_attempted = True
            try:
                client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    socket_timeout=3,
                    socket_connect_timeout=3,
                    retry_on_timeout=False,
                    protocol=2,
                )
                await asyncio.wait_for(client.ping(), timeout=3)
                self.redis = client
                logger.info("Redis connected")
            except Exception as e:
                self.redis = None
                logger.warning(f"Redis unavailable: {e}")
                if settings.REDIS_REQUIRED:
                    raise CacheUnavailableError(
                        f"Redis is required but unavailable: {e}"
                    ) from e
        return self.redis

    async def disconnect(self) -> None:
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            logger.info("Redis disconnected")

    def _ensure_policy(self, *, critical: bool = False) -> None:
        """critical=True 用于 token 黑名单/refresh 等安全路径。"""
        if self.redis is not None:
            return
        if settings.REDIS_REQUIRED or critical and settings.REDIS_REQUIRED:
            raise HTTPException(status_code=503, detail="Cache service unavailable")
        # 非 required：降级静默

    async def get(self, key: str, *, critical: bool = False) -> Any | None:
        if not self.redis:
            if settings.REDIS_REQUIRED:
                raise HTTPException(status_code=503, detail="Cache service unavailable")
            return None
        try:
            data = await asyncio.wait_for(self.redis.get(key), timeout=2)
            return json.loads(data) if data else None
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis get failed key={key}: {e}")
            if settings.REDIS_REQUIRED or critical:
                raise HTTPException(status_code=503, detail="Cache service unavailable") from e
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None, *, critical: bool = False) -> bool:
        if not self.redis:
            if settings.REDIS_REQUIRED or critical:
                raise HTTPException(status_code=503, detail="Cache service unavailable")
            return False
        try:
            ttl = ttl or settings.CACHE_TTL
            data = json.dumps(value, ensure_ascii=False, default=str)
            await asyncio.wait_for(self.redis.set(key, data, ex=ttl), timeout=2)
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis set failed key={key}: {e}")
            if settings.REDIS_REQUIRED or critical:
                raise HTTPException(status_code=503, detail="Cache service unavailable") from e
            return False

    async def delete(self, key: str, *, critical: bool = False) -> bool:
        if not self.redis:
            if settings.REDIS_REQUIRED or critical:
                raise HTTPException(status_code=503, detail="Cache service unavailable")
            return False
        try:
            await asyncio.wait_for(self.redis.delete(key), timeout=2)
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis delete failed key={key}: {e}")
            if settings.REDIS_REQUIRED or critical:
                raise HTTPException(status_code=503, detail="Cache service unavailable") from e
            return False


cache_manager = CacheManager()
