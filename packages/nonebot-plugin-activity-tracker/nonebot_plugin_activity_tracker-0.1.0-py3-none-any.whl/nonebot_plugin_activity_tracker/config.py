from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel

__all__ = ["NICKNAME", "Config", "global_config", "plugin_config"]


class Config(BaseModel):
    default_active_days: int = 7
    default_active_messages: int = 5

    redis_host: str | None = None
    redis_port: int | None = None


# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

# 全局名称
NICKNAME: str = next(iter(global_config.nickname), "")
