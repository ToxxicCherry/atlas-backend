from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload, joinedload
from app.models import ProductModel, TaskProductModel
from app.models.products import PositionModel
from app.schemas import ProductSchema
from typing import Sequence


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


async def fetch_cards_export(session: AsyncSession, task_id: UUID):
    yield '['

    query = (
        select(ProductModel)
        .join(TaskProductModel)
        .where(TaskProductModel.task_id == task_id)
        .options(selectinload(ProductModel.sizes))
        .execution_options(yield_per=500)

    )

    result = await session.stream_scalars(query)

    is_first_item = True

    async for product in result:
        if not is_first_item:
            yield ','
        else:
            is_first_item = False

        validated_product = ProductSchema.model_validate(product)
        json_string = validated_product.model_dump_json()
        yield json_string

    yield ']'



