from fastapi import FastAPI

from chargeguard.core.config import settings
from chargeguard.core.database import Base, engine
from chargeguard.models.dispute import Dispute  # noqa: F401 - registers table
from chargeguard.api.webhooks import router as webhook_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(webhook_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}