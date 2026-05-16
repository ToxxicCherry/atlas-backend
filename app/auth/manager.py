import uuid
import os
import dotenv
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, models
from app.models import UserModel
from app.db import get_user_db
from loguru import logger

dotenv.load_dotenv()
SECRET_KEY = os.getenv("SECRET")

class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:

        logger.success(f"User {user.id} has registered")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


