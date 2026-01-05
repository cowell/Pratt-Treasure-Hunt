from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .database import get_session, init_db
from .models import Clue, Find, Hunt, User, leaderboard_rows

app = FastAPI(
    title="Treasure Hunt API",
    description="Self-hosted backend for a prize-driven treasure hunt app.",
    version="0.2.0",
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


@app.post("/hunts", response_model=Hunt, status_code=status.HTTP_201_CREATED)
def create_hunt(hunt: Hunt, session: Annotated[Session, Depends(get_session)]) -> Hunt:
    session.add(hunt)
    session.commit()
    session.refresh(hunt)
    return hunt


@app.post("/clues", response_model=Clue, status_code=status.HTTP_201_CREATED)
def create_clue(clue: Clue, session: Annotated[Session, Depends(get_session)]) -> Clue:
    hunt = session.get(Hunt, clue.hunt_id)
    if not hunt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")
    session.add(clue)
    session.commit()
    session.refresh(clue)
    return clue


@app.post("/finds", response_model=Find, status_code=status.HTTP_201_CREATED)
def submit_find(find: Find, session: Annotated[Session, Depends(get_session)]) -> Find:
    user = session.get(User, find.user_id)
    clue = session.get(Clue, find.clue_id)
    if not user or not clue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or clue not found")

    normalized_answer = (find.submitted_answer or "").strip().lower()
    correct_answer = (clue.answer or "").strip().lower()
    find.correct = normalized_answer == correct_answer

    session.add(find)
    session.commit()
    session.refresh(find)
    return find


@app.get("/hunts/{hunt_id}/leaderboard", response_model=dict)
def hunt_leaderboard(
    hunt_id: int, session: Annotated[Session, Depends(get_session)]
) -> dict:
    hunt = session.exec(select(Hunt).where(Hunt.id == hunt_id)).first()
    if not hunt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hunt not found")

    session.refresh(hunt, attribute_names=["clues"])
    for clue in hunt.clues:
        session.refresh(clue, attribute_names=["finds"])

    return {"hunt_id": hunt.id, "title": hunt.title, "leaderboard": leaderboard_rows(hunt)}
