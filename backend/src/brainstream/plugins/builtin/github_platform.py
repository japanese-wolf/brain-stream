"""GitHub Platform plugin for GitHub Blog and Changelog feeds."""

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

GITHUB_BLOG_RSS_URL = "https://github.blog/feed/"
GITHUB_CHANGELOG_RSS_URL = "https://github.blog/changelog/feed/"


class GitHubPlatformPlugin(BaseSourcePlugin):
    """Plugin for fetching GitHub platform updates.

    This plugin fetches from GitHub's official blog and changelog,
    which includes:
    - GitHub product announcements
    - New feature releases
    - Platform changes and updates
    - GitHub Actions, Copilot, and other service updates
    """

    def __init__(
        self,
        blog_url: str = GITHUB_BLOG_RSS_URL,
        changelog_url: str = GITHUB_CHANGELOG_RSS_URL,
    ) -> None:
        self._blog_url = blog_url
        self._changelog_url = changelog_url

    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="github-platform",
            display_name="GitHub Platform Updates",
            vendor="GitHub",
            description="Fetches GitHub Blog and Changelog updates via RSS",
            source_type=SourceType.RSS,
            version="1.0.0",
            supported_tech_stack=[
                "github", "github-actions", "github-copilot",
                "github-pages", "github-packages", "codespaces",
            ],
        )

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        return True

    async def _fetch_feed(
        self,
        client: httpx.AsyncClient,
        feed_url: str,
        source_label: str,
        since: Optional[datetime] = None,
    ) -> list[RawArticle]:
        """Fetch and parse a single RSS feed."""
        articles: list[RawArticle] = []

        response = await client.get(feed_url)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        if feed.bozo and feed.bozo_exception:
            raise FetchError(
                self.info.name,
                f"RSS parsing error for {source_label}: {feed.bozo_exception}",
            )

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

            categories = ["github", source_label]
            if hasattr(entry, "tags"):
                categories.extend([tag.term for tag in entry.tags if hasattr(tag, "term")])

            article = RawArticle(
                external_id=entry.get("id", entry.get("link", "")),
                primary_source_url=entry.get("link", ""),
                original_title=entry.get("title", "Untitled"),
                original_content=entry.get("summary", entry.get("description", "")),
                published_at=published_at,
                vendor="GitHub",
                categories=categories,
                metadata={
                    "source": f"github-{source_label}",
                    "feed_url": feed_url,
                },
            )
            articles.append(article)

        return articles

    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch latest GitHub platform updates from Blog and Changelog.

        Args:
            since: Optional datetime to filter articles after this date.

        Returns:
            List of RawArticle objects.

        Raises:
            FetchError: If fetching fails.
        """
        try:
            all_articles: list[RawArticle] = []

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                blog_articles = await self._fetch_feed(client, self._blog_url, "blog", since)
                all_articles.extend(blog_articles)

                changelog_articles = await self._fetch_feed(
                    client, self._changelog_url, "changelog", since
                )
                all_articles.extend(changelog_articles)

            # Sort by published date (newest first)
            all_articles.sort(
                key=lambda a: a.published_at or datetime.min.replace(tzinfo=ZoneInfo("UTC")),
                reverse=True,
            )

            return all_articles

        except httpx.HTTPError as e:
            raise FetchError(self.info.name, f"HTTP error: {e}")
        except FetchError:
            raise
        except Exception as e:
            raise FetchError(self.info.name, f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if GitHub RSS feeds are accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.head(self._changelog_url)
                return response.status_code == 200
        except Exception:
            return False
