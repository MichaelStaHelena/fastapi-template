from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


def get_utc_now():
    return datetime.now(timezone.utc)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = Field(default="pending")
    priority: int = Field(default=1)
    created_at: datetime = Field(default_factory=get_utc_now)
