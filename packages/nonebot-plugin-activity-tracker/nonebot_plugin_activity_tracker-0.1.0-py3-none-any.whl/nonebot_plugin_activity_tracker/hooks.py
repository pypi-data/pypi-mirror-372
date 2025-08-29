import traceback

from nonebot.log import logger
from nonebot.message import event_preprocessor, run_preprocessor
from nonebot_plugin_alconna import UniMsg
from nonebot_plugin_uninfo import Uninfo

from .cache import cache

__all__ = ["record_active_session", "record_bot_active_session"]


@event_preprocessor
async def record_active_session(
        uni_msg: UniMsg,
        user_info: Uninfo,
):
    try:
        await cache.add(user_info)
    except Exception:
        logger.error(traceback.format_exc())


@run_preprocessor
async def record_bot_active_session(
        user_info: Uninfo,
):
    try:
        await cache.add(user_info, is_bot_active=True)
    except Exception:
        logger.error(traceback.format_exc())
