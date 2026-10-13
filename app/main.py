from time import perf_counter

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.config import settings
from app.controllers.health_controller import router as health_router
from app.controllers.user_controller import router as user_router
from app.logging_config import logger

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.settings = settings
app.include_router(health_router)
app.include_router(user_router)


@app.middleware("http")
async def log_requests(
	request: Request,
	call_next: RequestResponseEndpoint,
) -> Response:
	started_at = perf_counter()
	try:
		response = await call_next(request)
	except Exception:
		duration_ms = (perf_counter() - started_at) * 1000
		logger.exception(
			"Unhandled error for %s %s after %.2f ms",
			request.method,
			request.url.path,
			duration_ms,
		)
		raise

	duration_ms = (perf_counter() - started_at) * 1000
	logger.info(
		"%s %s -> %s (%.2f ms)",
		request.method,
		request.url.path,
		response.status_code,
		duration_ms,
	)
	return response