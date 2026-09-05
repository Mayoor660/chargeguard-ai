from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chargeguard.core.config import settings
from chargeguard.core.database import Base, engine
from chargeguard.models.dispute import Dispute  # noqa: F401 - registers table
from chargeguard.api.webhooks import router as webhook_router
from chargeguard.api.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(dashboard_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}