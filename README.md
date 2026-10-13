# Python REST API Demo

A small FastAPI starter organized into controller, service, model, repository, and database layers. It provides create and read endpoints for users, with records stored in SQLite.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

Runtime and development dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

## Setup

From the project root, sync the runtime and test dependencies:

```powershell
uv sync
```

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Settings are loaded by `app.config.settings` from `.env`, with process environment variables taking precedence. The `.env` file is ignored by Git and excluded from Docker; set production values in the deployment environment instead.

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `Python REST API` | FastAPI title |
| `APP_ENV` | `development` | Deployment environment name |
| `DEBUG` | `false` | FastAPI debug mode |
| `LOG_LEVEL` | `INFO` | Minimum log severity |
| `LOG_FILE` | `logs/app.log` | Log file path |
| `LOG_MAX_BYTES` | `5242880` | Maximum size of each log file (5 MiB) |
| `LOG_BACKUP_COUNT` | `3` | Number of rotated log files to retain |
| `DATABASE_PATH` | `data/app.db` | SQLite database file path |

Read a setting in application code with `from app.config import settings`, then access a property such as `settings.app_env`. The same object is available on requests as `request.app.state.settings`.

The application writes request summaries and unhandled errors to both the console and the rotating log file. Generated logs are ignored by Git. In Docker, logs are written to `/app/logs/app.log`; mount `/app/logs` as a volume to retain them after replacing the container.

## Run the API

```powershell
uv run --no-sync fastapi dev app/main.py
```

The API runs at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Test

```powershell
uv run --no-sync pytest
```

## Docker

Build and run the production image locally:

```powershell
docker build -t python-api-demo:local .
docker run --rm -p 8000:8000 -v python-api-logs:/app/logs -v python-api-data:/app/data python-api-demo:local
```

The API is available at `http://127.0.0.1:8000`, and the container health check calls `/health`.

## GitHub Actions deployment image

The Docker workflow builds and validates pull requests. Pushes to `main` and version tags such as `v1.0.0` publish the image to GitHub Container Registry (GHCR). The `main` image is also tagged `latest`; each build receives a commit SHA tag.

On a Docker server, pull and run the published image, replacing `your-github-owner` and `your-repository` with the GitHub owner and repository names:

```powershell
docker pull ghcr.io/your-github-owner/your-repository:latest
docker run -d --name python-api-demo --restart unless-stopped -p 8000:8000 -v python-api-logs:/app/logs -v python-api-data:/app/data ghcr.io/your-github-owner/your-repository:latest
```

For a private GHCR package, authenticate the server with a GitHub token that has `read:packages` permission before pulling. The workflow publishes the image; it does not deploy it to a server automatically.

## Endpoints

- `GET /health` reports whether the API process is responding.
- `POST /users` creates a user. JSON body: `{"name": "Ada Lovelace", "email": "ada@example.com"}`.
- `GET /users/{user_id}` returns a user or a `404` response when the ID is not found.

`SQLiteDatabase` stores user records in the file configured by `DATABASE_PATH`. The Docker command mounts `/app/data` in a named volume so records survive container replacement. Services depend on the `UserRepository` protocol, keeping the persistence implementation replaceable if the application later moves to a server database such as PostgreSQL.

## Project structure

```text
app/
  config.py      Environment-backed application settings
  database.py    SQLite database implementation
  controllers/   HTTP routes
  models/        Request and response models
  repositories/  SQLite data access
  services/      Application logic
  dependencies.py Repository and service wiring
  main.py        FastAPI application
tests/           API tests
pyproject.toml    uv project metadata and runtime/development dependencies
uv.lock           Locked uv dependencies
.env.example      Local environment settings template
Dockerfile        Production container image
.github/workflows/docker-publish.yml  GHCR build and publish workflow
```
