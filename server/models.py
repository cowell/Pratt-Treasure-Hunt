from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    name: str
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True

    habits: List["Habit"] = Relationship(back_populates="owner")
    checkins: List["CheckIn"] = Relationship(back_populates="user")


class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    title: str
    target_per_week: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    archived: bool = False

    owner: User = Relationship(back_populates="habits")
    checkins: List["CheckIn"] = Relationship(back_populates="habit")


class CheckIn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    habit_id: int = Field(foreign_key="habit.id")
    note: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="checkins")
    habit: Habit = Relationship(back_populates="checkins")


def weekly_habit_summary(habit: Habit, reference: Optional[datetime] = None) -> dict:
    """Return completion counts for the last 7 days."""
    now = reference or datetime.now(timezone.utc)
    window_start = now - timedelta(days=7)
    completions = [
        checkin for checkin in (habit.checkins or []) if checkin.created_at >= window_start
    ]
    return {
        "habit_id": habit.id,
        "title": habit.title,
        "target_per_week": habit.target_per_week,
        "completed_past_week": len(completions),
    }
