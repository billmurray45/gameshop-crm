from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional


class GameBase(BaseModel):
    name: str = Field(min_length=5, max_length=100)
    year: int = Field(ge=1990, le=2100)
    description: Optional[str] = Field(None, max_length=1500)
    platforms: Optional[list[str]] = Field(None, min_items=1, max_items=10)


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    year: Optional[int] = Field(None, ge=1990, le=2100)
    description: Optional[str] = Field(None, max_length=1500)
    platforms: Optional[list[str]] = Field(None, min_items=1, max_items=10)


class GameRead(GameBase):
    id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(from_attributes=True)