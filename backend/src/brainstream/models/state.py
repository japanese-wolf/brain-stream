"""Data models for Thompson Sampling state and feed items."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ClusterArm:
    """Thompson Sampling arm for a topic cluster."""

    cluster_id: int
    alpha: float = 1.0
    beta: float = 1.0
    article_count: int = 0
    label: str = ""
    updated_at: str = ""


@dataclass
class ActionLog:
    """User action log entry."""

    id: int
    article_id: str
    action: str  # 'click', 'skip', 'bookmark'
    cluster_id: int | None = None
    created_at: str = ""


@dataclass
class FeedItem:
    """Article in the feed with metadata."""

    id: str
    url: str
    title: str
    summary: str
    tags: list[str] = field(default_factory=list)
    vendor: str = ""
    is_primary_source: bool = False
    cluster_id: int = -1
    published_at: str = ""
    collected_at: str = ""
    source_plugin: str = ""


@dataclass
class ClusterInfo:
    """Information about a topic cluster."""

    cluster_id: int
    article_count: int
    density: float
    label: str = ""
    alpha: float = 1.0
    beta: float = 1.0
    sample_titles: list[str] = field(default_factory=list)
