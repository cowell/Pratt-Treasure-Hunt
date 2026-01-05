# Fitness accountability app (self-hosted backend)

This repository starts a self-hosted FastAPI backend for a fitness accountability Android app. The API tracks users, weekly habits, and check-ins so your mobile app can deliver streaks, leaderboards, and team challenges without relying on third-party clouds.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --reload
```

The server defaults to SQLite at `app.db`. Override with `DATABASE_URL` (e.g., `postgresql://…`) before starting.

## Example requests

Create a user:
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","name":"Alex","timezone":"UTC"}'
```

Add a habit for that user:
```bash
curl -X POST http://localhost:8000/habits \
  -H "Content-Type: application/json" \
  -d '{"owner_id":1,"title":"Morning run","target_per_week":4}'
```

Record a check-in:
```bash
curl -X POST http://localhost:8000/checkins \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"habit_id":1,"note":"5km loop"}'
```

Retrieve a weekly summary:
```bash
curl http://localhost:8000/users/1/summary
```

## Tests

Run the FastAPI test suite (uses an in-memory SQLite database):

```bash
pytest
```
