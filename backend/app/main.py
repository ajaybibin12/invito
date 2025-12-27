from fastapi import FastAPI
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.init_admin import create_admin_if_not_exists
from sqlalchemy.orm import Session

from app.api.v1.auth import router as auth_router
from app.api.v1.events import router as events_router
from app.api.v1.invites import router as invite_router


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(invite_router)


@app.on_event("startup")
def startup_event():
    db: Session = SessionLocal()
    try:
        create_admin_if_not_exists(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENV
    }
