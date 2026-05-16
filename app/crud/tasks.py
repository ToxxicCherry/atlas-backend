from app.schemas import CreateTaskSchema, TaskStatus
from app.models import TaskModel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional, Sequence

async def create_task(session: AsyncSession, task: CreateTaskSchema, user_id: UUID):
    query = (
        insert(TaskModel)
        .values(
            user_id=user_id,
            source=task.source,
            type=task.task_type,
            payload=task.payload.model_dump()
        ).returning(TaskModel)
    )

    result = await session.execute(query)
    await session.commit()
    created_task = result.scalar_one_or_none()
    return created_task


async def get_user_tasks(
        session: AsyncSession,
        user_id: UUID,
        limit: int,
        offset: int,
        status: Optional[TaskStatus] = None
) -> Sequence[TaskModel]:

    query = select(TaskModel).where(TaskModel.user_id == user_id)

    if status is not None:
        query = query.where(TaskModel.status == status)

    query = query.order_by(TaskModel.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks

async def get_task_for_user(session: AsyncSession, user_id: UUID, task_id: UUID) -> Optional[TaskModel]:
    query = select(TaskModel).where(TaskModel.user_id == user_id, TaskModel.id == task_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


