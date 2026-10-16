from fastapi import APIRouter
from app.logging_config import logger

router = APIRouter(tags=["health"])
logger.info("Health controller initialized")

@router.get("/health")
def health_check() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}