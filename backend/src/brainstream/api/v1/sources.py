"""Data source API endpoints."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from brainstream.core.database import get_db
from brainstream.models.article import DataSource
from brainstream.plugins.registry import registry
from brainstream.services import collect_all

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceResponse(BaseModel):
    """Response schema for a data source."""

    id: str
    plugin_name: str
    name: str
    vendor: str
    enabled: bool
    fetch_status: str
    last_fetched_at: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class PluginResponse(BaseModel):
    """Response schema for available plugins."""

    name: str
    display_name: str
    vendor: str
    description: str
    source_type: str
    version: str


class SourceUpdate(BaseModel):
    """Schema for updating a data source."""

    enabled: Optional[bool] = None
    config: Optional[dict] = None


@router.get("/plugins", response_model=list[PluginResponse])
async def list_plugins() -> list[PluginResponse]:
    """List all available data source plugins.

    Returns:
        List of available plugins
    """
    plugins = registry.list_plugins()
    return [
        PluginResponse(
            name=p.name,
            display_name=p.display_name,
            vendor=p.vendor,
            description=p.description,
            source_type=p.source_type.value,
            version=p.version,
        )
        for p in plugins
    ]


@router.get("", response_model=list[SourceResponse])
async def list_sources(
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[SourceResponse]:
    """List configured data sources.

    Args:
        enabled_only: Only return enabled sources

    Returns:
        List of configured data sources
    """
    query = select(DataSource)
    if enabled_only:
        query = query.where(DataSource.enabled == True)

    result = await db.execute(query)
    sources = result.scalars().all()

    return [SourceResponse.model_validate(s) for s in sources]


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> SourceResponse:
    """Get a single data source by ID.

    Args:
        source_id: Data source UUID

    Returns:
        Data source details

    Raises:
        HTTPException: If source not found
    """
    query = select(DataSource).where(DataSource.id == source_id)
    result = await db.execute(query)
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")

    return SourceResponse.model_validate(source)


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: str,
    update: SourceUpdate,
    db: AsyncSession = Depends(get_db),
) -> SourceResponse:
    """Update a data source configuration.

    Args:
        source_id: Data source UUID
        update: Fields to update

    Returns:
        Updated data source

    Raises:
        HTTPException: If source not found
    """
    query = select(DataSource).where(DataSource.id == source_id)
    result = await db.execute(query)
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")

    if update.enabled is not None:
        source.enabled = update.enabled

    if update.config is not None:
        source.config = update.config

    await db.commit()
    await db.refresh(source)

    return SourceResponse.model_validate(source)


@router.post("/process")
async def trigger_process(
    limit: int = 50,
) -> dict:
    """Process existing unprocessed articles with LLM.

    Args:
        limit: Maximum number of articles to process.

    Returns:
        Processing results.
    """
    from brainstream.core.config import settings
    from brainstream.services import process_unprocessed

    config_path = settings.data_dir / "config.json"
    tech_stack: list[str] = []
    if config_path.exists():
        config = json.loads(config_path.read_text())
        tech_stack = config.get("tech_stack", [])

    try:
        result = await process_unprocessed(tech_stack=tech_stack, limit=limit)
        return {
            "status": "success",
            "total": result.total,
            "processed": result.processed,
            "failed": result.failed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch")
async def trigger_fetch_all() -> dict:
    """Trigger a fetch from all enabled sources.

    Returns:
        Collection summary with results per source.
    """
    from brainstream.core.config import settings

    tech_stack: list[str] = []
    config_path = settings.data_dir / "config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text())
        tech_stack = config.get("tech_stack", [])

    try:
        summary = await collect_all(tech_stack=tech_stack)
        return {
            "status": "success",
            "total_fetched": summary.total_fetched,
            "total_new": summary.total_new,
            "sources": [
                {
                    "source_name": s.source_name,
                    "fetched": s.fetched,
                    "new": s.new,
                    "processed": s.processed,
                    "errors": s.errors,
                }
                for s in summary.sources
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{source_id}/fetch")
async def trigger_fetch(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Manually trigger a fetch for a data source.

    Args:
        source_id: Data source UUID

    Returns:
        Status message

    Raises:
        HTTPException: If source not found or fetch fails
    """
    query = select(DataSource).where(DataSource.id == source_id)
    result = await db.execute(query)
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Get plugin
    plugin = registry.get(source.plugin_name)
    if not plugin:
        raise HTTPException(status_code=500, detail=f"Plugin not found: {source.plugin_name}")

    # Fetch updates
    try:
        articles = await plugin.fetch_updates(since=source.last_fetched_at)
        return {
            "status": "success",
            "fetched": len(articles),
            "source": source.name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
