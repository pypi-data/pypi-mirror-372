from nonebot import get_driver, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_orm")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")

from nonebot_plugin_uninfo import Uninfo

from .cache import ActivityData, cache
from .config import Config
from .database import load_sessions_to_cache, save_cache_to_database
from .hooks import record_active_session as record_active_session
from .hooks import record_bot_active_session as record_bot_active_session

__plugin_meta__ = PluginMetadata(
    name="会话活跃追踪",
    description="基于nonebot的会话活跃检测插件，只对活跃会话推送信息",
    usage="",
    type="library",
    homepage="https://github.com/zifox666/nonebot-plugin-activity-tracker",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_uninfo"),
)


driver = get_driver()


@driver.on_startup
async def init():
    await load_sessions_to_cache()


@driver.on_shutdown
async def shutdown():
    await save_cache_to_database()


async def query_session_active(adapter: str, scene_type: str, scene_id: str) -> ActivityData | None:
    """
    检查会话是否活跃
    :param adapter: 适配器名称
    :param scene_type: 场景类型
    :param scene_id: 场景ID

    :return: 如果活跃，返回对应的 ActivityData，否则返回 None
    """
    return await cache.query(adapter, scene_type, scene_id)


async def get_all_active_sessions() -> list[ActivityData]:
    """
    获取所有活跃会话数据
    :return: 活跃会话数据列表 ActivityData
    """
    return await cache.get_all()


async def get_session_activity(uninfo: Uninfo) -> ActivityData | None:
    """
    依赖注入函数：获取当前会话活跃数据
    :param uninfo: 当前会话的 Uninfo 对象
    :return: 如果活跃，返回对应的 ActivityData，否则返回 None
    """
    return await cache.get(uninfo)
