import uuid
from fastapi_users import schemas
from pydantic import EmailStr


class UserReadSchema(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreateSchema(schemas.BaseUserCreate):
    email: EmailStr
    password: str


class UserUpdateSchema(schemas.BaseUserUpdate):
    pass