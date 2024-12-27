import datetime
from typing import Literal
from pydantic import BaseModel


class ItemRequest(BaseModel):
    id: int


class GetAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author: str
    created_at: datetime.datetime


class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: int
    author: str


class CreateAdvertisementResponse(ItemRequest):
    pass


class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    author: str | None = None


class UpdateAdvertisementResponse(ItemRequest):
    pass


class StatusResponse(BaseModel):
    status: Literal['deleted']


class GetAdvertisementQueryRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    author: str | None = None


class GetAdvertisementQueryResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author: str
