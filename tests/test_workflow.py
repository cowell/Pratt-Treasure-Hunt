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
    user_payload = {"email": "alex@example.com", "display_name": "Alex"}
    user_response = client.post("/users", json=user_payload)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    hunt_payload = {
        "title": "Downtown Dash",
        "description": "Solve the clues to win!",
        "reward": "$50 gift card",
        "active": True,
    }
    hunt_response = client.post("/hunts", json=hunt_payload)
    assert hunt_response.status_code == 201
    hunt_id = hunt_response.json()["id"]

    clue_payload = {
        "hunt_id": hunt_id,
        "prompt": "Red door on Main St",
        "answer": "lantern",
        "order": 1,
    }
    clue_response = client.post("/clues", json=clue_payload)
    assert clue_response.status_code == 201
    clue_id = clue_response.json()["id"]

    find_response = client.post(
        "/finds",
        json={"user_id": user_id, "clue_id": clue_id, "submitted_answer": "Lantern"},
    )
    assert find_response.status_code == 201
    assert find_response.json()["correct"] is True

    leaderboard_response = client.get(f"/hunts/{hunt_id}/leaderboard")
    assert leaderboard_response.status_code == 200
    leaderboard = leaderboard_response.json()["leaderboard"]
    assert leaderboard[0]["user_id"] == user_id
    assert leaderboard[0]["score"] == 1


def test_leaderboard_deduplicates_repeated_correct_finds() -> None:
    user_payload = {"email": "jordan@example.com", "display_name": "Jordan"}
    user_response = client.post("/users", json=user_payload)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    hunt_payload = {
        "title": "Library Quest",
        "description": "Find the hidden wisdom.",
        "reward": "Sticker pack",
        "active": True,
    }
    hunt_response = client.post("/hunts", json=hunt_payload)
    assert hunt_response.status_code == 201
    hunt_id = hunt_response.json()["id"]

    clue_payload = {
        "hunt_id": hunt_id,
        "prompt": "Look under the big oak",
        "answer": "book",
        "order": 1,
    }
    clue_response = client.post("/clues", json=clue_payload)
    assert clue_response.status_code == 201
    clue_id = clue_response.json()["id"]

    first_find_response = client.post(
        "/finds",
        json={"user_id": user_id, "clue_id": clue_id, "submitted_answer": "Book"},
    )
    assert first_find_response.status_code == 201
    assert first_find_response.json()["correct"] is True

    second_find_response = client.post(
        "/finds",
        json={"user_id": user_id, "clue_id": clue_id, "submitted_answer": "book"},
    )
    assert second_find_response.status_code == 201
    assert second_find_response.json()["correct"] is True

    leaderboard_response = client.get(f"/hunts/{hunt_id}/leaderboard")
    assert leaderboard_response.status_code == 200
    leaderboard = leaderboard_response.json()["leaderboard"]
    assert leaderboard[0]["user_id"] == user_id
    assert leaderboard[0]["score"] == 1
