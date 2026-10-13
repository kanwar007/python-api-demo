# Python REST API Demo

A small FastAPI starter organized into controller, service, model, and repository layers. It provides create and read endpoints for users and stores data in memory.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

The project runtime dependency is declared in `pyproject.toml` and locked in `uv.lock`. `requirements.txt` also lists the API and test dependencies.

## Setup

From the project root, sync the project dependencies and install the test dependencies:

```powershell
uv sync
uv pip install -r requirements.txt
```

## Run the API

```powershell
uv run --no-sync fastapi dev app/main.py
```

The API runs at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Test

```powershell
uv run --no-sync pytest
```

## Endpoints

- `POST /users` creates a user. JSON body: `{"name": "Ada Lovelace", "email": "ada@example.com"}`.
- `GET /users/{user_id}` returns a user or a `404` response when the ID is not found.

The in-memory data is reset whenever the API process restarts.

## Project structure

```text
app/
  controllers/   HTTP routes
  models/        Request and response models
  repositories/  In-memory data access
  services/      Application logic
  main.py        FastAPI application
tests/           API tests
pyproject.toml    uv project metadata and runtime dependencies
uv.lock           Locked uv dependencies
requirements.txt  Runtime and test dependency list
```
