"""Base plugin interface for data sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class SourceType(str, Enum):
    """Type of data source."""

    RSS = "rss"
    API = "api"
    SCRAPING = "scraping"
    BIGQUERY = "bigquery"


@dataclass
class RawArticle:
    """Raw article data fetched from a source.

    This represents unprocessed data before LLM summarization.
    """

    external_id: str
    """Unique identifier from the source (for deduplication)."""

    primary_source_url: str
    """URL to the original article (required)."""

    original_title: str
    """Original title from the source."""

    original_content: str
    """Original content/description."""

    published_at: Optional[datetime] = None
    """Publication date if available."""

    vendor: str = ""
    """Vendor name (e.g., 'AWS', 'GCP', 'OpenAI')."""

    categories: list[str] = field(default_factory=list)
    """Categories/tags from the source."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata from the source."""


@dataclass
class PluginInfo:
    """Information about a plugin."""

    name: str
    display_name: str
    vendor: str
    description: str
    source_type: SourceType
    version: str = "1.0.0"
    supported_tech_stack: list[str] = field(default_factory=list)


class BaseSourcePlugin(ABC):
    """Abstract base class for data source plugins."""

    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        ...

    @abstractmethod
    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        ...

    @abstractmethod
    def validate_config(self) -> bool:
        ...

    def get_config_schema(self) -> Optional[dict[str, Any]]:
        return None

    async def health_check(self) -> bool:
        try:
            return self.validate_config()
        except Exception:
            return False


class PluginError(Exception):
    """Base exception for plugin errors."""

    def __init__(self, plugin_name: str, message: str):
        self.plugin_name = plugin_name
        self.message = message
        super().__init__(f"[{plugin_name}] {message}")


class FetchError(PluginError):
    pass


class ConfigError(PluginError):
    pass
