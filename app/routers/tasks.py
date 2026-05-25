import redis.asyncio as aioredis
import asyncio
from fastapi import APIRouter, Depends, Query, HTTPException, WebSocket, WebSocketDisconnect, WebSocketException, status as f_status
from app.auth import current_user, get_current_user_websocket
from app.models import UserModel
from app.schemas import CreateTaskSchema, TaskReadSchema, TaskStatus, ProductSchema, TaskType, ProductPositionSchema, ParseResultSchema
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
        page: int = Query(1, ge=1, le=50),
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),
):
    limit = 100
    offset = (page - 1) * limit
    tasks = await crud.get_user_tasks(db, user.id, limit, offset, status)
    return tasks

@router.get("/{task_id}/results", status_code=200, response_model=list[ProductSchema])
async def get_fetch_cards_results(
        task_id: UUID,
        page: int = Query(1, ge=1, le=50),
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

    limit = 100
    offset = (page - 1) * limit
    products = await crud.get_fetch_cards_results(db, task_id, limit, offset)
    return products

@router.get("/{task_id}/positions", status_code=200, response_model=list[ProductPositionSchema])
async def get_positions_results(
        task_id: UUID,
        page: int = Query(1, ge=1, le=50),
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

    limit = 100
    offset = (page - 1) * limit
    positions = await crud.get_track_positions_results(db, task_id, limit, offset)
    return positions

@router.websocket("/ws/{task_id}")
async def task_websocket_endpoint(
        websocket: WebSocket,
        task_id: UUID,
        redis: aioredis.Redis = Depends(get_redis),
        user: UserModel = Depends(get_current_user_websocket),
        db: AsyncSession = Depends(get_async_session)
):

    task_check = await crud.get_task_for_user(db, user.id, task_id)
    if not task_check:
        raise WebSocketException(code=f_status.WS_1008_POLICY_VIOLATION)

    await websocket.accept()
    logger.info(f"[WebSocket] Клиент подключился к задаче: {task_id}")

    pubsub = redis.pubsub()
    channel_name = f"task_updates:{task_id}"

    try:
        await pubsub.subscribe(channel_name)
        logger.info(f"[WebSocket] Успешная подписка на Redis канал: {channel_name}")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)

            if message:
                raw_data = message["data"].decode('utf-8')
                parsed_data = ParseResultSchema.model_validate_json(raw_data)
                await websocket.send_json(parsed_data.model_dump_json())

                if parsed_data.status in (TaskStatus.completed, TaskStatus.failed):
                    logger.info(f"[WebSocket] Задача {task_id} завершена. Закрываем соединение.")
                    break
            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Пользователь разорвал соединение для задачи {task_id}")

    except Exception as e:
        logger.error(f"[WebSocket] Ошибка в работе вебсокета: {e}")

    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
        logger.info(f"[WebSocket] Освобождены ресурсы подписки для задачи {task_id}")


