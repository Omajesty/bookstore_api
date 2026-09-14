"""Pydantic schemas: request bodies and response shapes for /docs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    bio: Optional[str] = None


class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    bio: Optional[str] = None


class AuthorOut(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    author_id: int


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    author_id: Optional[int] = None


class BookOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    author_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    message: str
