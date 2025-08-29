from datetime import datetime
import traceback

from nonebot import logger
from nonebot_plugin_orm import Model, get_session
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column

from .cache import ActivityData, cache
from .config import plugin_config


class ActivitySession(Model):
    __tablename__ = "activity_sessions"

    adapter: Mapped[str] = mapped_column(String(50), primary_key=True)
    scene_type: Mapped[str] = mapped_column(String(50), primary_key=True)
    scene_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    last_session_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_bot_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


async def load_sessions_to_cache():
    """从数据库加载会话数据到缓存"""
    try:
        session = get_session()
        async with session.begin():
            stmt = select(ActivitySession)
            result = await session.execute(stmt)
            sessions = result.scalars().all()

            logger.info(f"正在从数据库加载 {len(sessions)} 条活跃会话数据到缓存...")

            for session_data in sessions:
                if session_data.last_session_activity:
                    days_passed = (datetime.now() - session_data.last_session_activity).days
                    if days_passed > plugin_config.default_active_days:
                        continue

                activity_data = ActivityData(
                    adapter=session_data.adapter,
                    scene_type=session_data.scene_type,
                    scene_id=session_data.scene_id,
                    count=session_data.count,
                    last_session_activity=session_data.last_session_activity,
                    last_bot_activity=session_data.last_bot_activity,
                )

                elapsed_seconds = int((datetime.now() - session_data.last_session_activity).total_seconds())
                remaining_ttl = max(cache.ttl - elapsed_seconds, 60)

                await cache.set(
                    activity_data.session_key,
                    session_data.count,
                    ttl=remaining_ttl
                )

                if session_data.last_bot_activity:
                    await cache.set(activity_data.bot_key, session_data.last_bot_activity.timestamp())

            logger.info("活跃会话数据加载完成")

    except Exception as e:
        logger.error(f"加载活跃会话数据失败: {e}\n{traceback.format_exc()}")


async def save_cache_to_database():
    """将缓存数据保存到数据库"""
    try:
        cache_data = await cache.get_all()

        if not cache_data:
            logger.info("没有缓存数据需要保存")
            return

        logger.info(f"正在保存 {len(cache_data)} 条缓存数据到数据库...")

        session = get_session()
        async with session.begin():
            for data in cache_data:
                stmt = select(ActivitySession).where(
                    ActivitySession.adapter == data.adapter,
                    ActivitySession.scene_type == data.scene_type,
                    ActivitySession.scene_id == data.scene_id
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    existing.count = data.count
                    existing.last_session_activity = data.last_session_activity
                    existing.last_bot_activity = data.last_bot_activity
                    existing.updated_at = datetime.now()
                else:
                    new_session = ActivitySession(
                        adapter=data.adapter,
                        scene_type=data.scene_type,
                        scene_id=data.scene_id,
                        count=data.count,
                        last_session_activity=data.last_session_activity,
                        last_bot_activity=data.last_bot_activity,
                    )
                    session.add(new_session)

            logger.info("缓存数据保存完成")

    except Exception as e:
        logger.error(f"保存缓存数据失败: {e}\n{traceback.format_exc()}")
