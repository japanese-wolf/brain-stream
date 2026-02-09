"""Feed API endpoints."""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from brainstream.services.feed import FeedSelector

router = APIRouter(tags=["feed"])


class FeedItemResponse(BaseModel):
    id: str
    url: str
    title: str
    summary: str
    tags: list[str]
    vendor: str
    is_primary_source: bool
    cluster_id: int
    published_at: str
    collected_at: str
    source_plugin: str


class FeedResponse(BaseModel):
    items: list[FeedItemResponse]
    total: int


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    vendor: Optional[str] = Query(default=None),
    primary_only: bool = Query(default=False),
):
    """Get the article feed using Thompson Sampling."""
    selector = FeedSelector()
    items = selector.generate_feed(
        limit=limit,
        vendor_filter=vendor,
        primary_only=primary_only,
        offset=offset,
    )

    return FeedResponse(
        items=[
            FeedItemResponse(
                id=item.id,
                url=item.url,
                title=item.title,
                summary=item.summary,
                tags=item.tags,
                vendor=item.vendor,
                is_primary_source=item.is_primary_source,
                cluster_id=item.cluster_id,
                published_at=item.published_at,
                collected_at=item.collected_at,
                source_plugin=item.source_plugin,
            )
            for item in items
        ],
        total=len(items),
    )
