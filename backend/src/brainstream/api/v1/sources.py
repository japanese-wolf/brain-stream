"""Data sources API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from brainstream.plugins.registry import registry

router = APIRouter(tags=["sources"])


class SourceResponse(BaseModel):
    name: str
    display_name: str
    vendor: str
    description: str
    source_type: str


class SourcesListResponse(BaseModel):
    sources: list[SourceResponse]


@router.get("/sources", response_model=SourcesListResponse)
async def list_sources():
    """List all available data source plugins."""
    plugins = registry.list_plugins()

    return SourcesListResponse(
        sources=[
            SourceResponse(
                name=p.name,
                display_name=p.display_name,
                vendor=p.vendor,
                description=p.description,
                source_type=p.source_type.value,
            )
            for p in plugins
        ]
    )
