"""GCP Release Notes RSS feed plugin."""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import feedparser
import httpx

from brainstream.plugins.base import (
    BaseSourcePlugin,
    FetchError,
    PluginInfo,
    RawArticle,
    SourceType,
)

# GCP Release Notes RSS Feed URL
GCP_RELEASE_NOTES_RSS_URL = "https://cloud.google.com/feeds/gcp-release-notes.xml"


class GCPReleaseNotesPlugin(BaseSourcePlugin):
    """Plugin for fetching GCP Release Notes via RSS.

    This plugin fetches the latest GCP release notes from the official
    Google Cloud RSS feed, which includes:
    - New product launches
    - Feature updates
    - Breaking changes
    - Deprecations
    """

    def __init__(self, feed_url: str = GCP_RELEASE_NOTES_RSS_URL) -> None:
        """Initialize the plugin.

        Args:
            feed_url: RSS feed URL (can be overridden for testing).
        """
        self._feed_url = feed_url

    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="gcp-release-notes",
            display_name="GCP Release Notes",
            vendor="GCP",
            description="Fetches Google Cloud Platform release notes via RSS feed",
            source_type=SourceType.RSS,
            version="1.0.0",
            supported_tech_stack=[
                # Compute
                "cloud-run", "gke", "compute-engine", "cloud-functions", "app-engine",
                # Storage
                "cloud-storage", "filestore", "persistent-disk",
                # Database
                "cloud-sql", "firestore", "bigtable", "spanner", "memorystore",
                # AI/ML
                "vertex-ai", "vision-ai", "natural-language", "automl",
                # Analytics
                "bigquery", "dataflow", "dataproc", "pub-sub",
                # Networking
                "cloud-cdn", "cloud-dns", "cloud-load-balancing", "vpc",
                # Security
                "iam", "secret-manager", "cloud-kms",
            ],
        )

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        return True

    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch latest GCP release notes from RSS feed.

        Args:
            since: Optional datetime to filter articles after this date.

        Returns:
            List of RawArticle objects.

        Raises:
            FetchError: If fetching or parsing fails.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self._feed_url)
                response.raise_for_status()
                content = response.text

            feed = feedparser.parse(content)

            if feed.bozo and feed.bozo_exception:
                raise FetchError(
                    self.info.name,
                    f"RSS parsing error: {feed.bozo_exception}",
                )

            articles: list[RawArticle] = []

            for entry in feed.entries:
                published_at = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published_at = datetime(*entry.updated_parsed[:6], tzinfo=ZoneInfo("UTC"))

                if since and published_at:
                    # Ensure both datetimes are timezone-aware for comparison
                    since_aware = since if since.tzinfo else since.replace(tzinfo=ZoneInfo("UTC"))
                    if published_at < since_aware:
                        continue

                categories = []
                if hasattr(entry, "tags"):
                    categories = [tag.term for tag in entry.tags if hasattr(tag, "term")]

                article = RawArticle(
                    external_id=entry.get("id", entry.get("link", "")),
                    primary_source_url=entry.get("link", ""),
                    original_title=entry.get("title", "Untitled"),
                    original_content=entry.get("summary", entry.get("description", "")),
                    published_at=published_at,
                    vendor="GCP",
                    categories=categories,
                    metadata={
                        "source": "gcp-release-notes",
                        "feed_url": self._feed_url,
                    },
                )
                articles.append(article)

            return articles

        except httpx.HTTPError as e:
            raise FetchError(self.info.name, f"HTTP error: {e}")
        except Exception as e:
            raise FetchError(self.info.name, f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if GCP RSS feed is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(self._feed_url)
                return response.status_code == 200
        except Exception:
            return False
