from datetime import datetime
from enum import Enum
from typing import Optional, List, Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# Base Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


# Response Schemas
class TaskRead(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


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
