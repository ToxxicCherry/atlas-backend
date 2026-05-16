from .base import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import relationship, Mapped



class UserModel(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"


    tasks: Mapped[list['TaskModel']] = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")