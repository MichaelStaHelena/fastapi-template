from typing import Any
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Base Schemas (Shared attributes)
class JutsuBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    chakra_cost: int = Field(..., ge=1, description="Chakra cost of the jutsu")


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    village: str = Field(..., min_length=1, max_length=50)
    rank: Optional[str] = Field(None, max_length=50)


# Request Schemas (For creating or updating)
class JutsuCreate(JutsuBase):
    pass


class JutsuUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    chakra_cost: Optional[int] = Field(None, ge=1)


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    village: Optional[str] = Field(None, min_length=1, max_length=50)
    rank: Optional[str] = Field(None, max_length=50)


# Response Schemas (For returning data)
class JutsuRead(JutsuBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CharacterRead(CharacterBase):
    id: int
    created_at: datetime
    updated_at: datetime
    jutsus: List[JutsuRead] = []

    class Config:
        orm_mode = True


# Pagination Schemas
class PageParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")


class PageResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @property
    def next_page(self) -> Optional[int]:
        if self.has_next:
            return self.page + 1
        return None

    @property
    def prev_page(self) -> Optional[int]:
        if self.has_prev:
            return self.page - 1
        return None