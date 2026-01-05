from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .database import get_session, init_db
from .models import CheckIn, Habit, User, weekly_habit_summary

app = FastAPI(
    title="Fitness Habit API",
    description="Self-hosted backend for the accountability Android app.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, session: Annotated[Session, Depends(get_session)]) -> User:
    email_exists = session.exec(select(User).where(User.email == user.email)).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/habits", response_model=Habit, status_code=status.HTTP_201_CREATED)
def create_habit(habit: Habit, session: Annotated[Session, Depends(get_session)]) -> Habit:
    owner = session.get(User, habit.owner_id)
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@app.post("/checkins", response_model=CheckIn, status_code=status.HTTP_201_CREATED)
def create_checkin(
    checkin: CheckIn, session: Annotated[Session, Depends(get_session)]
) -> CheckIn:
    user = session.get(User, checkin.user_id)
    habit = session.get(Habit, checkin.habit_id)
    if not user or not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or habit not found")
    session.add(checkin)
    session.commit()
    session.refresh(checkin)
    return checkin


@app.get("/users/{user_id}/summary", response_model=dict)
def user_summary(
    user_id: int, session: Annotated[Session, Depends(get_session)]
) -> dict:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    habits: List[Habit] = session.exec(select(Habit).where(Habit.owner_id == user_id)).all()
    for habit in habits:
        session.refresh(habit, attribute_names=["checkins"])

    summaries = [weekly_habit_summary(habit) for habit in habits]
    return {"user_id": user.id, "name": user.name, "habits": summaries}
