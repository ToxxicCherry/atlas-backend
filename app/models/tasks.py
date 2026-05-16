from .base import Base
from sqlalchemy import DateTime, func, text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import uuid4, UUID
from app.schemas import TaskStatus, MarketPlace, TaskType
from datetime import datetime




class TaskModel(Base):
    __tablename__ = 'tasks'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    source: Mapped[MarketPlace] = mapped_column(Enum(MarketPlace, name='market_place'), default=MarketPlace.wildberries)
    type: Mapped[TaskType] = mapped_column(Enum(TaskType), name='task_type', default=TaskType.fetch_cards)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, name='task_status'), default=TaskStatus.pending)
    priority: Mapped[int] = mapped_column(default=0)
    payload: Mapped[dict] = mapped_column(JSONB)
    total_found: Mapped[int | None]
    error_message: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None]= mapped_column(DateTime(timezone=True))

    user: Mapped["UserModel"] = relationship('UserModel', back_populates='tasks')
    positions: Mapped['PositionModel'] = relationship('PositionModel', back_populates='task')


