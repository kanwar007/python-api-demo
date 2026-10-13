# Python REST API Demo

A small FastAPI starter organized into controller, service, model, and repository layers. The sample exposes create and read endpoints for users and uses an in-memory repository.

## Project structure

```text
app/
	controllers/   HTTP routes
	models/        Request and response models
	repositories/  Data access
	services/      Application logic
	main.py        FastAPI application
tests/           API tests
requirements.txt
```

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive documentation is at `/docs`.

## Test

```powershell
python -m pytest
```
