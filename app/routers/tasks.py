import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query, HTTPException
from app.auth import current_user
from app.models import UserModel
from app.schemas import CreateTaskSchema, TaskReadSchema, TaskStatus, ProductSchema, TaskType, ProductPositionSchema
from app.db import get_async_session
from app.core import get_redis
from app import crud
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from loguru import logger

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/create", status_code=201, response_model=TaskReadSchema)
async def create_task(
        task: CreateTaskSchema,
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),
        redis: aioredis.Redis = Depends(get_redis),

):

    created_task = await crud.create_task(db, task, user.id)
    task_id = str(created_task.id)
    await redis.lpush('tasks_queue', task_id)
    logger.success(f"Created task {task_id}")
    return created_task

@router.get("/my", status_code=200, response_model=list[TaskReadSchema])
async def get_user_tasks(
        status: Optional[TaskStatus] = None,
        limit: int = Query(10, ge=1, le=100),
        offset: int = 0,
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),
):
    tasks = await crud.get_user_tasks(db, user.id, limit, offset, status)
    return tasks

@router.get("/{task_id}/results", status_code=200, response_model=list[ProductSchema])
async def get_fetch_cards_results(
        task_id: UUID,
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),
):

    task_check = await crud.get_task_for_user(db, user.id, task_id)

    if not task_check:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    if task_check.type != TaskType.fetch_cards:
        raise HTTPException(
            status_code=422,
            detail="Invalid task type",
        )

    if task_check.status != TaskStatus.completed:
        raise HTTPException(
            status_code=400,
            detail=f"Task is in status '{task_check.status.value}'. Please wait for completion."
        )

    products = await crud.get_fetch_cards_results(db, task_id)
    return products

@router.get("/{task_id}/positions", status_code=200, response_model=list[ProductPositionSchema])
async def get_positions_results(
        task_id: UUID,
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),
):
    task_check = await crud.get_task_for_user(db, user.id, task_id)

    if not task_check:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    if task_check.type != TaskType.track_positions:
        raise HTTPException(
            status_code=422,
            detail="Invalid task type",
        )

    if task_check.status != TaskStatus.completed:
        raise HTTPException(
            status_code=400,
            detail=f"Task is in status '{task_check.status.value}'. Please wait for completion."
        )

    positions = await crud.get_track_positions_results(db, task_id)
    return positions
