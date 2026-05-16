from fastapi import APIRouter, Depends, Query, HTTPException
from app.auth import current_user
from app.models import UserModel
from app.schemas import CreateTaskSchema, TaskReadSchema, TaskStatus, ProductSchema
from app.db import get_async_session
from app import crud
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/create", status_code=201, response_model=TaskReadSchema)
async def create_task(
        task: CreateTaskSchema,
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),

):

    created_task = await crud.create_task(db, task, user.id)
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
async def get_task_results(
        task_id: UUID,
        user: UserModel = Depends(current_user),
        db: AsyncSession = Depends(get_async_session),
):

    task_check = await crud.get_task_for_user(db, user.id, task_id)

    if not task_check:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    if task_check.status != TaskStatus.completed:
        raise HTTPException(
            status_code=400,
            detail=f"Task is in status '{task_check.status.value}'. Please wait for completion."
        )

    products = await crud.get_task_results(db, task_id, task_check.type)
    return products