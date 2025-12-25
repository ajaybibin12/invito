from fastapi import FastAPI
from app.api.v1.auth import router as auth_router

from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENV
    }
