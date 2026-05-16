import dotenv
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from app.models import UserModel


dotenv.load_dotenv()
DEV_DB_URL = os.getenv("DEV_DB_URL")


engine = create_async_engine(
    url=DEV_DB_URL,
    poolclass=NullPool,
    #echo=True
)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session



async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserModel)