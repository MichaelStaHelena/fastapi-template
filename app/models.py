from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship


def get_utc_now():
    return datetime.now(timezone.utc)

class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    village: str = Field(index=True)
    rank: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    # Relationship to Jutsu
    jutsus: List["Jutsu"] = Relationship(back_populates="character")


class Jutsu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    chakra_cost: int = Field(default=10)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    # Foreign key to Character
    character_id: Optional[int] = Field(default=None, foreign_key="character.id")
    character: Optional[Character] = Relationship(back_populates="jutsus")