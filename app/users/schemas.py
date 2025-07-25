from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import date
from typing import Optional
from fastapi import UploadFile


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=6, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    birthday: Optional[date] = Field(None)
    avatar: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=30)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=6, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=30)
    birthday: Optional[date] = Field(None)
    avatar: Optional[UploadFile] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)
