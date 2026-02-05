"""Anthropic API Changelog plugin."""

import hashlib
import re
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

from brainstream.plugins.base import (
    BaseSourcePlugin,
    FetchError,
    PluginInfo,
    RawArticle,
    SourceType,
)

# Anthropic Release Notes URL
ANTHROPIC_CHANGELOG_URL = "https://docs.anthropic.com/en/release-notes/overview"


class AnthropicChangelogPlugin(BaseSourcePlugin):
    """Plugin for fetching Anthropic API Changelog.

    This plugin scrapes the Anthropic release notes page, which includes:
    - Claude model updates
    - API changes and new features
    - Breaking changes
    - Deprecations
    """

    def __init__(self, changelog_url: str = ANTHROPIC_CHANGELOG_URL) -> None:
        """Initialize the plugin.

        Args:
            changelog_url: Changelog URL (can be overridden for testing).
        """
        self._changelog_url = changelog_url

    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="anthropic-changelog",
            display_name="Anthropic API Changelog",
            vendor="Anthropic",
            description="Fetches Anthropic API release notes by scraping their documentation",
            source_type=SourceType.SCRAPING,
            version="1.0.0",
            supported_tech_stack=[
                "anthropic", "claude", "claude-3", "claude-opus", "claude-sonnet",
                "claude-haiku", "messages-api", "tool-use", "vision",
            ],
        )

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        return True

    def _generate_external_id(self, title: str, date_str: str) -> str:
        """Generate a unique external ID for an entry."""
        content = f"{title}-{date_str}"
        return f"anthropic-{hashlib.md5(content.encode()).hexdigest()[:12]}"

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from changelog.

        Anthropic uses formats like "January 15, 2024", "2024-01-15", etc.
        """
        date_formats = [
            "%B %d, %Y",     # January 15, 2024
            "%b %d, %Y",     # Jan 15, 2024
            "%Y-%m-%d",      # 2024-01-15
            "%d %B %Y",      # 15 January 2024
            "%d %b %Y",      # 15 Jan 2024
        ]

        # Clean up the date string
        date_str = date_str.strip().replace(",", ", ").replace("  ", " ")

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=ZoneInfo("UTC"))
            except ValueError:
                continue
        return None

    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch latest Anthropic changelog entries by scraping.

        Args:
            since: Optional datetime to filter articles after this date.

        Returns:
            List of RawArticle objects.

        Raises:
            FetchError: If fetching or parsing fails.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; BrainStream/1.0; +https://github.com/xxx/brain-stream)"
            }

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self._changelog_url, headers=headers)
                response.raise_for_status()
                html = response.text

            soup = BeautifulSoup(html, "lxml")
            articles: list[RawArticle] = []

            # Look for date patterns in the page
            date_pattern = re.compile(
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}',
                re.IGNORECASE
            )

            # Find sections that look like changelog entries
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'article', 'section']):
                text = element.get_text(strip=True)
                date_match = date_pattern.search(text)

                if date_match:
                    date_str = date_match.group(0)
                    published_at = self._parse_date(date_str)

                    if since and published_at:
                        since_aware = since if since.tzinfo else since.replace(tzinfo=ZoneInfo("UTC"))
                        if published_at < since_aware:
                            continue

                    # Extract title from the element
                    title = text
                    if len(title) > 200:
                        title = title[:200] + "..."

                    # Get content from the element and its siblings
                    content_parts = []

                    # Try to get content from nested elements
                    for child in element.find_all(['p', 'li', 'div']):
                        child_text = child.get_text(strip=True)
                        if child_text and len(child_text) > 10:
                            content_parts.append(child_text)
                        if len(content_parts) > 10:
                            break

                    # If no nested content, try siblings
                    if not content_parts:
                        next_elem = element.find_next_sibling()
                        while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
                            elem_text = next_elem.get_text(strip=True)
                            if elem_text and not date_pattern.match(elem_text):
                                content_parts.append(elem_text)
                            next_elem = next_elem.find_next_sibling()
                            if len(content_parts) > 10:
                                break

                    content = " ".join(content_parts) if content_parts else title

                    if not content or len(content) < 20:
                        continue

                    external_id = self._generate_external_id(title, date_str)

                    article = RawArticle(
                        external_id=external_id,
                        primary_source_url=self._changelog_url,
                        original_title=title,
                        original_content=content,
                        published_at=published_at,
                        vendor="Anthropic",
                        categories=["api", "changelog", "claude"],
                        metadata={
                            "source": "anthropic-changelog",
                            "url": self._changelog_url,
                        },
                    )
                    articles.append(article)

            # Deduplicate by external_id
            seen_ids = set()
            unique_articles = []
            for article in articles:
                if article.external_id not in seen_ids:
                    seen_ids.add(article.external_id)
                    unique_articles.append(article)

            return unique_articles

        except httpx.HTTPError as e:
            raise FetchError(self.info.name, f"HTTP error: {e}")
        except Exception as e:
            raise FetchError(self.info.name, f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if Anthropic changelog is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.head(self._changelog_url)
                return response.status_code == 200
        except Exception:
            return False
