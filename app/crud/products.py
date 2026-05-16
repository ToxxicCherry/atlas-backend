from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import ProductModel, TaskProductModel
from app.schemas import TaskType
from typing import Sequence
from loguru import logger


async def get_fetch_cards_results(session: AsyncSession, task_id: UUID) -> Sequence[ProductModel]:
    query = (
        select(ProductModel)
        .join(TaskProductModel)
        .where(TaskProductModel.task_id == task_id)
        .options(selectinload(ProductModel.sizes))
    )

    result = await session.execute(query)
    products = result.scalars().all()
    return products

async def get_track_positions_results(session: AsyncSession, task_id: UUID):
    raise NotImplementedError


async def get_task_results(session: AsyncSession, task_id: UUID, task_type: TaskType):
    result_fetchers = {
        TaskType.fetch_cards: get_fetch_cards_results,
        TaskType.track_positions: get_track_positions_results,
    }

    return await result_fetchers[task_type](session, task_id)