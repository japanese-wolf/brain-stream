"""Article detail and action endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from brainstream.services.feed import FeedSelector
from brainstream.services.topology import TopologyEngine

router = APIRouter(tags=["articles"])


class ArticleResponse(BaseModel):
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
    tech_domain: str


class ActionRequest(BaseModel):
    action: str  # 'click', 'bookmark', 'skip'


class ActionResponse(BaseModel):
    success: bool
    message: str


class TopologyCluster(BaseModel):
    cluster_id: int
    article_count: int
    density: float
    label: str
    alpha: float
    beta: float
    sample_titles: list[str]


class TopologyResponse(BaseModel):
    total_articles: int
    clusters: list[TopologyCluster]


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    """Get article details."""
    topology = TopologyEngine()
    article = topology.get_article(article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    tags_str = article.get("tags", "")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

    return ArticleResponse(
        id=article["id"],
        url=article.get("url", ""),
        title=article.get("original_title", ""),
        summary=article.get("summary", ""),
        tags=tags,
        vendor=article.get("vendor", ""),
        is_primary_source=bool(article.get("is_primary_source", False)),
        cluster_id=article.get("cluster_id", -1),
        published_at=article.get("published_at", ""),
        collected_at=article.get("collected_at", ""),
        source_plugin=article.get("source_plugin", ""),
        tech_domain=article.get("tech_domain", ""),
    )


@router.post("/articles/{article_id}/action", response_model=ActionResponse)
async def record_action(article_id: str, request: ActionRequest):
    """Record a user action (click, bookmark, skip) for Thompson Sampling."""
    if request.action not in ("click", "bookmark", "skip"):
        raise HTTPException(status_code=400, detail="Invalid action. Use: click, bookmark, skip")

    selector = FeedSelector()
    selector.record_action(article_id, request.action)

    return ActionResponse(
        success=True,
        message=f"Action '{request.action}' recorded for article {article_id}",
    )


@router.get("/topology", response_model=TopologyResponse)
async def get_topology():
    """Get information space topology (clusters and their properties)."""
    topology = TopologyEngine()
    clusters = topology.get_topology_info()

    return TopologyResponse(
        total_articles=topology.get_total_articles(),
        clusters=[
            TopologyCluster(
                cluster_id=c.cluster_id,
                article_count=c.article_count,
                density=c.density,
                label=c.label,
                alpha=c.alpha,
                beta=c.beta,
                sample_titles=c.sample_titles,
            )
            for c in clusters
        ],
    )


@router.post("/collect")
async def trigger_collection():
    """Manually trigger article collection from all sources."""
    from brainstream.services.collector import collect_all

    summary = await collect_all()

    return {
        "total_fetched": summary.total_fetched,
        "total_new": summary.total_new,
        "total_processed": summary.total_processed,
        "duration_ms": summary.duration_ms,
        "sources": [
            {
                "name": s.source_name,
                "fetched": s.fetched,
                "new": s.new,
                "processed": s.processed,
                "errors": s.errors,
            }
            for s in summary.sources
        ],
    }
