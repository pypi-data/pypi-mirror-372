from datetime import datetime, timedelta
import traceback
from typing import Any

from aiocache import Cache as aic
from nonebot.log import logger
from nonebot_plugin_uninfo import Uninfo
from pydantic import BaseModel, Field

from .config import plugin_config

__all__ = ["DAY", "HOUR", "ActivityData", "cache"]

HOUR = 60 * 60
DAY = 24 * HOUR


class ActivityData(BaseModel):
    adapter: str
    scene_type: str
    scene_id: str
    count: int
    last_session_activity: datetime | None = None
    last_bot_activity: datetime | None = None
    key_prefix: str = Field(default="activity_tracker:")

    @classmethod
    def from_cache_result(
        cls, key: str, value: int, ttl: int, last_bot_activity: datetime | None, cache_ttl: int
    ) -> "ActivityData":
        """从缓存结果创建 ActivityData 实例"""
        parts = key.split(":")
        if len(parts) >= 4:
            _, method, adapter, scene_type, scene_id = parts[:5]
        else:
            adapter, scene_type, scene_id = parts[-3:]

        last_session_activity = None
        if ttl > 0:
            seconds_since_activity = cache_ttl - ttl
            last_session_activity = datetime.now() - timedelta(seconds=seconds_since_activity)

        return cls(
            adapter=adapter,
            scene_type=scene_type,
            scene_id=scene_id,
            count=value,
            last_session_activity=last_session_activity,
            last_bot_activity=last_bot_activity,
        )

    @classmethod
    def from_uninfo(
        cls,
        uninfo: Uninfo,
        count: int = 0,
        last_session_activity: datetime | None = None,
        last_bot_activity: datetime | None = None,
    ) -> "ActivityData":
        """从用户信息创建 ActivityData 实例"""
        return cls(
            adapter=uninfo.adapter.name,
            scene_type=uninfo.scene.type.name,
            scene_id=uninfo.scene.id,
            count=count,
            last_session_activity=last_session_activity,
            last_bot_activity=last_bot_activity,
        )

    @classmethod
    def from_query(
        cls,
        adapter: str,
        scene_type: str,
        scene_id: str,
        count: int = 0,
        last_session_activity: datetime | None = None,
        last_bot_activity: datetime | None = None,
    ) -> "ActivityData":
        """从查询参数创建 ActivityData 实例"""
        return cls(
            adapter=adapter,
            scene_type=scene_type,
            scene_id=scene_id,
            count=count,
            last_session_activity=last_session_activity,
            last_bot_activity=last_bot_activity,
        )

    @property
    def session_key(self) -> str:
        """生成会话缓存键"""
        return f"{self.key_prefix}session:{self.adapter}:{self.scene_type}:{self.scene_id}"

    @property
    def bot_key(self) -> str:
        """生成机器人活跃缓存键"""
        return f"{self.key_prefix}bot:{self.adapter}:{self.scene_type}:{self.scene_id}"

    def __str__(self) -> str:
        last_session_str = (
            self.last_session_activity.strftime("%Y-%m-%d %H:%M:%S") if self.last_session_activity else "未知"
        )
        last_bot_str = self.last_bot_activity.strftime("%Y-%m-%d %H:%M:%S") if self.last_bot_activity else "未知"

        return (
            f"适配器: {self.adapter}\n"
            f"场景类型: {self.scene_type}\n"
            f"场景ID: {self.scene_id}\n"
            f"消息计数: {self.count}\n"
            f"最后活跃时间: {last_session_str}\n"
            f"机器人最后活跃: {last_bot_str}"
        )


class Cache:
    def __init__(self):
        if not plugin_config.redis_host:
            self._cache = aic(aic.MEMORY)
        else:
            self._cache = aic(aic.REDIS, endpoint=plugin_config.redis_host, port=plugin_config.redis_port)

        self.ttl: int = plugin_config.default_active_days * DAY
        self.redis: bool = bool(plugin_config.redis_host)
        self.key_prefix: str = "activity_tracker:"

    async def _get_ttl(self, key: str) -> int:
        """获取键的TTL，处理不同缓存类型"""
        if not self.redis:
            return self.ttl
        else:
            try:
                result = await self._cache.raw("TTL", key)
                return result if result > 0 else self.ttl
            except Exception:
                return self.ttl

    async def get(self, uninfo: Uninfo) -> ActivityData | None:
        activity_data = ActivityData.from_uninfo(uninfo)
        value = await self._cache.get(activity_data.session_key)
        if value is None:
            return None

        ttl = await self._get_ttl(activity_data.session_key)
        last_bot_activity = await self._cache.get(activity_data.bot_key)

        return ActivityData.from_cache_result(
            key=activity_data.session_key, value=value, ttl=ttl, last_bot_activity=last_bot_activity, cache_ttl=self.ttl
        )

    async def add(self, uninfo: Uninfo, is_bot_active: bool = False) -> int:
        current_data = await self.get(uninfo)
        count = current_data.count if current_data else 0

        activity_data = ActivityData.from_uninfo(uninfo, count + 1)

        r = await self._cache.set(
            key=activity_data.session_key,
            value=count + 1,
            ttl=self.ttl,
        )

        if is_bot_active:
            # 修复：将 datetime 转换为时间戳进行存储
            await self._cache.set(
                key=activity_data.bot_key,
                value=datetime.now().timestamp(),
            )

        return count + 1 if r else count

    async def remove(self, uninfo: Uninfo) -> None:
        activity_data = ActivityData.from_uninfo(uninfo)
        await self._cache.delete(activity_data.session_key)
        await self._cache.delete(activity_data.bot_key)

    async def get_all(self) -> list[ActivityData]:
        if not self.redis:
            keys = [key for key in self._cache._cache.keys() if key.startswith(f"{self.key_prefix}session:")]
        else:
            try:
                keys = await self._cache.raw("keys", f"{self.key_prefix}session:*")
                if not isinstance(keys, list):
                    keys = []
            except Exception:
                logger.error(f"{traceback.format_exc()}")
                return []

        if not keys:
            return []

        values = await self._cache.multi_get(keys)
        result = []

        for key, value in zip(keys, values):
            if value is None:
                continue

            key_str = key.decode() if isinstance(key, bytes) else key
            parts = key_str[len(self.key_prefix) :].split(":")
            if len(parts) < 4 or parts[0] != "session":
                continue

            _, adapter, scene_type, scene_id = parts[:4]
            bot_key = f"{self.key_prefix}bot:{adapter}:{scene_type}:{scene_id}"
            last_bot_activity_timestamp = await self._cache.get(bot_key)

            last_bot_activity = None
            if last_bot_activity_timestamp:
                try:
                    last_bot_activity = datetime.fromtimestamp(last_bot_activity_timestamp)
                except (ValueError, TypeError):
                    last_bot_activity = None

            ttl = await self._get_ttl(key_str)

            activity_data = ActivityData.from_cache_result(
                key=key_str, value=value, ttl=ttl, last_bot_activity=last_bot_activity, cache_ttl=self.ttl
            )
            result.append(activity_data)

        return result

    async def set(self, key: str, value: Any, ttl: int = 0) -> None:
        if ttl <= 0:
            await self._cache.set(key, value)
        else:
            await self._cache.set(key, value, ttl=ttl)

    async def query(self, adapter: str, scene_type: str, scene_id: str) -> ActivityData | None:
        temp_data = ActivityData.from_query(adapter, scene_type, scene_id)

        value = await self._cache.get(temp_data.session_key)
        if value is None:
            return None

        ttl = await self._get_ttl(temp_data.session_key)
        last_bot_activity_timestamp = await self._cache.get(temp_data.bot_key)

        last_bot_activity = None
        if last_bot_activity_timestamp:
            try:
                last_bot_activity = datetime.fromtimestamp(last_bot_activity_timestamp)
            except (ValueError, TypeError):
                last_bot_activity = None

        return ActivityData.from_cache_result(
            key=temp_data.session_key, value=value, ttl=ttl, last_bot_activity=last_bot_activity, cache_ttl=self.ttl
        )


cache = Cache()
