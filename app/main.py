from fastapi import FastAPI

from app.controllers.user_controller import router as user_router

app = FastAPI(title="Python REST API")
app.include_router(user_router)