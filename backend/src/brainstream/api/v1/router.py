"""Main API v1 router."""

from fastapi import APIRouter

from brainstream.api.v1.articles import router as articles_router
from brainstream.api.v1.profile import router as profile_router
from brainstream.api.v1.sources import router as sources_router

router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(articles_router)
router.include_router(sources_router)
router.include_router(profile_router)
