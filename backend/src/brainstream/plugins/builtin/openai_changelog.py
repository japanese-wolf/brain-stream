"""OpenAI API Changelog plugin."""

import hashlib
import re
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import feedparser
import httpx
from bs4 import BeautifulSoup

from brainstream.plugins.base import (
    BaseSourcePlugin,
    FetchError,
    PluginInfo,
    RawArticle,
    SourceType,
)

# OpenAI Changelog URLs - try multiple sources
OPENAI_CHANGELOG_URL = "https://platform.openai.com/docs/changelog"
OPENAI_BLOG_RSS_URL = "https://openai.com/blog/rss.xml"


class OpenAIChangelogPlugin(BaseSourcePlugin):
    """Plugin for fetching OpenAI API Changelog.

    This plugin scrapes the OpenAI API changelog page, which includes:
    - API updates and new endpoints
    - Model releases and updates
    - Breaking changes
    - Deprecations
    """

    def __init__(self, changelog_url: str = OPENAI_CHANGELOG_URL) -> None:
        """Initialize the plugin.

        Args:
            changelog_url: Changelog URL (can be overridden for testing).
        """
        self._changelog_url = changelog_url

    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="openai-changelog",
            display_name="OpenAI API Changelog",
            vendor="OpenAI",
            description="Fetches OpenAI API changelog by scraping their documentation",
            source_type=SourceType.SCRAPING,
            version="1.0.0",
            supported_tech_stack=[
                "openai", "gpt-4", "gpt-3.5", "dall-e", "whisper",
                "embeddings", "fine-tuning", "assistants", "chat-completions",
            ],
        )

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        return True

    def _generate_external_id(self, title: str, date_str: str) -> str:
        """Generate a unique external ID for an entry."""
        content = f"{title}-{date_str}"
        return f"openai-{hashlib.md5(content.encode()).hexdigest()[:12]}"

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from changelog.

        OpenAI uses formats like "January 15, 2024" or "Jan 15, 2024"
        """
        date_formats = [
            "%B %d, %Y",  # January 15, 2024
            "%b %d, %Y",  # Jan 15, 2024
            "%Y-%m-%d",   # 2024-01-15
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=ZoneInfo("UTC"))
            except ValueError:
                continue
        return None

    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch latest OpenAI updates from blog RSS feed.

        Falls back to blog RSS since the changelog page blocks scrapers.

        Args:
            since: Optional datetime to filter articles after this date.

        Returns:
            List of RawArticle objects.

        Raises:
            FetchError: If fetching or parsing fails.
        """
        try:
            # Use the blog RSS feed as primary source
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(OPENAI_BLOG_RSS_URL)
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
                    since_aware = since if since.tzinfo else since.replace(tzinfo=ZoneInfo("UTC"))
                    if published_at < since_aware:
                        continue

                categories = ["openai", "blog"]
                if hasattr(entry, "tags"):
                    categories.extend([tag.term for tag in entry.tags if hasattr(tag, "term")])

                article = RawArticle(
                    external_id=entry.get("id", entry.get("link", "")),
                    primary_source_url=entry.get("link", ""),
                    original_title=entry.get("title", "Untitled"),
                    original_content=entry.get("summary", entry.get("description", "")),
                    published_at=published_at,
                    vendor="OpenAI",
                    categories=categories,
                    metadata={
                        "source": "openai-blog",
                        "feed_url": OPENAI_BLOG_RSS_URL,
                    },
                )
                articles.append(article)

            return articles

        except httpx.HTTPError as e:
            raise FetchError(self.info.name, f"HTTP error: {e}")
        except Exception as e:
            raise FetchError(self.info.name, f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if OpenAI blog RSS is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.head(OPENAI_BLOG_RSS_URL)
                return response.status_code == 200
        except Exception:
            return False
