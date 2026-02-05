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
    """Unique plugin identifier (e.g., 'aws-whatsnew')."""

    display_name: str
    """Human-readable name (e.g., 'AWS What's New')."""

    vendor: str
    """Vendor name (e.g., 'AWS')."""

    description: str
    """Brief description of what this plugin fetches."""

    source_type: SourceType
    """Type of data source."""

    version: str = "1.0.0"
    """Plugin version."""

    supported_tech_stack: list[str] = field(default_factory=list)
    """List of tech stack identifiers this plugin is relevant for."""


class BaseSourcePlugin(ABC):
    """Abstract base class for data source plugins.

    All data source plugins must inherit from this class and implement
    the required abstract methods.

    Example:
        ```python
        class AWSWhatsNewPlugin(BaseSourcePlugin):
            @property
            def info(self) -> PluginInfo:
                return PluginInfo(
                    name="aws-whatsnew",
                    display_name="AWS What's New",
                    vendor="AWS",
                    description="Fetches AWS What's New announcements via RSS",
                    source_type=SourceType.RSS,
                )

            async def fetch_updates(self) -> list[RawArticle]:
                # Fetch and return articles
                ...

            def validate_config(self) -> bool:
                return True
        ```
    """

    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Return plugin metadata.

        Returns:
            PluginInfo containing name, vendor, description, etc.
        """
        ...

    @abstractmethod
    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch updates from the data source.

        Args:
            since: Optional datetime to fetch updates after. If None, fetch recent updates.

        Returns:
            List of RawArticle objects representing fetched updates.

        Raises:
            PluginError: If fetching fails.
        """
        ...

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if configuration is valid, False otherwise.
        """
        ...

    def get_config_schema(self) -> Optional[dict[str, Any]]:
        """Return JSON Schema for plugin configuration.

        Override this method to provide configuration options.

        Returns:
            JSON Schema dict or None if no configuration is needed.
        """
        return None

    async def health_check(self) -> bool:
        """Check if the plugin can connect to its data source.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            # Default implementation: try to fetch with validation
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
    """Error during data fetching."""

    pass


class ConfigError(PluginError):
    """Error in plugin configuration."""

    pass
