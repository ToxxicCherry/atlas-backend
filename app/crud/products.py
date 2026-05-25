from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload, joinedload
from app.models import ProductModel, TaskProductModel
from app.models.products import PositionModel
from app.schemas import TaskType
from typing import Sequence
from loguru import logger


async def get_fetch_cards_results(session: AsyncSession, task_id: UUID, limit: int, offset: int) -> Sequence[ProductModel]:
    query = (
        select(ProductModel)
        .join(TaskProductModel)
        .where(TaskProductModel.task_id == task_id)
        .options(selectinload(ProductModel.sizes))
        .limit(limit)
        .offset(offset)

    )

    result = await session.execute(query)
    products = result.scalars().all()
    return products

async def get_track_positions_results(session: AsyncSession, task_id: UUID, limit: int, offset: int):
    query = (
        select(PositionModel)
        .distinct(PositionModel.product_id)
        .options(
            joinedload(PositionModel.product)
            .options(selectinload(ProductModel.sizes))

        )
        .where(PositionModel.task_id == task_id)
        .order_by(
            PositionModel.product_id,
            desc(PositionModel.created_at)
        )
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(query)
    return result.scalars().all()

