from pydantic import (
                    BaseModel,
                    Field,
                    ConfigDict,
                    )
from typing import List, Union, Literal, Annotated
from .enums import TaskType, MarketPlace
from uuid import UUID
from datetime import datetime
from app.schemas import TaskStatus



class FetchCardsPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: Literal[TaskType.fetch_cards] = TaskType.fetch_cards
    query: str

class TrackPositionPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: Literal[TaskType.track_positions] = TaskType.track_positions
    query: str
    articles: List[int]



class CreateTaskSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    source: MarketPlace = Field(default=MarketPlace.wildberries.value)
    payload: Annotated[
        Union[FetchCardsPayload, TrackPositionPayload],
        Field(discriminator='type')
        ]

    @property
    def task_type(self) -> TaskType:
        return self.payload.type

class TaskReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    source: MarketPlace
    status: TaskStatus
    type: TaskType
    payload: Annotated[
        Union[FetchCardsPayload, TrackPositionPayload],
        Field(discriminator='type')
    ]
    created_at: datetime

