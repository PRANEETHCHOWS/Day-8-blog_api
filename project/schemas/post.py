from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., max_length=10000)
    tags: List[str] = Field(default_factory=list, max_length=5)
    author_id: int = Field(..., gt=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title cannot be empty")
        return value.strip()


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    tags: Optional[List[str]] = Field(None, max_length=5)

    @field_validator("title")
    @classmethod
    def validate_optional_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("title cannot be empty")
        return value.strip()


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

