from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import health, auth, pairing, habits, checkins, feed


api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(pairing.router)
api_router.include_router(habits.router)
api_router.include_router(checkins.router)
api_router.include_router(feed.router)
