from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth_backend, fastapi_users
from app.schemas import UserReadSchema, UserCreateSchema
from app.models import  Base
from app.db import engine
from app.routers import tasks_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield



app = FastAPI(
    title="Atlas DaaS Backend",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
    prefix="/auth",
    tags=["auth"],
)



app.include_router(tasks_router, tags=["tasks"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)