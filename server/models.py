from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    display_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True

    finds: List["Find"] = Relationship(back_populates="user")


class Hunt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    reward: str = ""
    active: bool = True
    ends_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    clues: List["Clue"] = Relationship(back_populates="hunt")


class Clue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hunt_id: int = Field(foreign_key="hunt.id")
    prompt: str
    answer: str
    order: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    hunt: Hunt = Relationship(back_populates="clues")
    finds: List["Find"] = Relationship(back_populates="clue")


class Find(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    clue_id: int = Field(foreign_key="clue.id")
    submitted_answer: str
    correct: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="finds")
    clue: Clue = Relationship(back_populates="finds")


def leaderboard_rows(hunt: Hunt) -> List[dict]:
    """Return leaderboard rows for a hunt based on correct finds."""
    scores = {}
    counted_pairs = set()
    for clue in hunt.clues or []:
        for find in clue.finds or []:
            if not find.correct:
                continue
            pair = (find.user_id, find.clue_id)
            if pair in counted_pairs:
                continue
            counted_pairs.add(pair)
            scores.setdefault(find.user_id, 0)
            scores[find.user_id] += 1
    rows = [
        {"user_id": user_id, "score": score}
        for user_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ]
    return rows
