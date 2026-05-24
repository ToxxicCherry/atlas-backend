import os
import dotenv
import uuid
from app.models import UserModel
from .manager import get_user_manager, UserManager
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users import FastAPIUsers
from fastapi import WebSocket, Depends, WebSocketException, status
from loguru import logger


dotenv.load_dotenv()
SECRET = os.getenv("SECRET")
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)


fastapi_users = FastAPIUsers[UserModel, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)

async def get_current_user_websocket(
        websocket: WebSocket,
        token: str | None = None,
        user_manager: UserManager = Depends(get_user_manager)
):

    if not token:
        logger.warning("[WebSocket Auth] Токен отсутствует в Query-параметрах")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    strategy = auth_backend.get_strategy()
    user = await strategy.read_token(token, user_manager)

    if user is None or not user.is_active:
        logger.warning(f"[WebSocket Auth] Невалидный или неактивный токен: {token[:10]}...")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user

