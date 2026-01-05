# Treasure Hunt Prizes (self-hosted backend)

This repository now provides a self-hosted FastAPI backend for a prize-driven treasure hunt app. Players join hunts, solve clues, and submit answers to climb leaderboards. You control rewards and hosting so you’re not locked into third-party platforms.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --reload
```

The server defaults to SQLite at `app.db`. Override with `DATABASE_URL` (e.g., `postgresql://…`) before starting.

## Example requests

Create a player:
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","display_name":"Alex"}'
```

Create a hunt:
```bash
curl -X POST http://localhost:8000/hunts \
  -H "Content-Type: application/json" \
  -d '{"title":"City Secrets","description":"Solve clues downtown","reward":"$100 gift","active":true}'
```

Add a clue to that hunt (simple answer match for demo purposes):
```bash
curl -X POST http://localhost:8000/clues \
  -H "Content-Type: application/json" \
  -d '{"hunt_id":1,"prompt":"Find the red door on Main St","answer":"lantern"}'
```

Submit an answer (case-insensitive):
```bash
curl -X POST http://localhost:8000/finds \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"clue_id":1,"submitted_answer":"Lantern"}'
```

Retrieve leaderboard for a hunt:
```bash
curl http://localhost:8000/hunts/1/leaderboard
```

## Tests

Run the FastAPI test suite (uses an in-memory SQLite database):

```bash
pytest
```
