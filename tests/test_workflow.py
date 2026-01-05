import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from server.database import engine
from server.main import app

client = TestClient(app)


def setup_module() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_user_flow() -> None:
    user_payload = {"email": "alex@example.com", "name": "Alex", "timezone": "UTC"}
    user_response = client.post("/users", json=user_payload)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    habit_payload = {
        "owner_id": user_id,
        "title": "Morning run",
        "target_per_week": 4,
    }
    habit_response = client.post("/habits", json=habit_payload)
    assert habit_response.status_code == 201
    habit_id = habit_response.json()["id"]

    checkin_response = client.post(
        "/checkins",
        json={"user_id": user_id, "habit_id": habit_id, "note": "5km loop"},
    )
    assert checkin_response.status_code == 201

    summary = client.get(f"/users/{user_id}/summary")
    assert summary.status_code == 200
    summary_body = summary.json()
    assert summary_body["user_id"] == user_id
    assert summary_body["habits"][0]["completed_past_week"] == 1
