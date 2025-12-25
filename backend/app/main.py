from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENV
    }
