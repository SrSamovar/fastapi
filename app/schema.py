import datetime
import uuid
from typing import Literal
from pydantic import BaseModel


class ItemResponse(BaseModel):
    id: int


class BaseUserRequest(BaseModel):
    name: str
    password: str


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


class CreateAdvertisementResponse(ItemResponse):
    pass


class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    author: str | None = None


class UpdateAdvertisementResponse(ItemResponse):
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


class UserRequest(BaseUserRequest):
    pass


class UserResponse(ItemResponse):
    pass


class LoginResponse(BaseModel):
    token: uuid.UUID


class LoginRequest(BaseUserRequest):
    pass


class GetUserResponse(BaseModel):
    id: int
    name: str
    role: str


class UpdateUserResponse(ItemResponse):
    pass


class UpdateUserRequest(BaseModel):
    name: str | None = None
    password: str | None = None
