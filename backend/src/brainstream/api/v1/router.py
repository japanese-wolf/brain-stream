"""API router combining all endpoint modules."""

from fastapi import APIRouter

from brainstream.api.v1.articles import router as articles_router
from brainstream.api.v1.feed import router as feed_router
from brainstream.api.v1.sources import router as sources_router

router = APIRouter(prefix="/api/v1")

router.include_router(feed_router)
router.include_router(articles_router)
router.include_router(sources_router)
