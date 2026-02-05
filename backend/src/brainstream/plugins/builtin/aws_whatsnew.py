"""AWS What's New RSS feed plugin."""

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

# AWS What's New RSS Feed URL
AWS_WHATSNEW_RSS_URL = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"


class AWSWhatsNewPlugin(BaseSourcePlugin):
    """Plugin for fetching AWS What's New announcements via RSS.

    This plugin fetches the latest AWS announcements from the official
    AWS What's New RSS feed, which includes:
    - New service launches
    - Feature updates
    - Regional expansions
    - Pricing changes
    """

    def __init__(self, feed_url: str = AWS_WHATSNEW_RSS_URL) -> None:
        """Initialize the plugin.

        Args:
            feed_url: RSS feed URL (can be overridden for testing).
        """
        self._feed_url = feed_url

    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="aws-whatsnew",
            display_name="AWS What's New",
            vendor="AWS",
            description="Fetches AWS What's New announcements via RSS feed",
            source_type=SourceType.RSS,
            version="1.0.0",
            supported_tech_stack=[
                # Compute
                "lambda", "ec2", "ecs", "eks", "fargate", "lightsail",
                # Storage
                "s3", "ebs", "efs", "glacier",
                # Database
                "rds", "dynamodb", "aurora", "redshift", "elasticache",
                # Networking
                "vpc", "cloudfront", "route53", "api-gateway",
                # AI/ML
                "sagemaker", "bedrock", "comprehend", "rekognition",
                # Analytics
                "athena", "kinesis", "glue", "emr",
                # Security
                "iam", "cognito", "kms", "secrets-manager",
            ],
        )

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        # No special configuration needed for RSS
        return True

    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch latest AWS announcements from RSS feed.

        Args:
            since: Optional datetime to filter articles after this date.

        Returns:
            List of RawArticle objects.

        Raises:
            FetchError: If fetching or parsing fails.
        """
        try:
            # Fetch RSS feed
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self._feed_url)
                response.raise_for_status()
                content = response.text

            # Parse RSS
            feed = feedparser.parse(content)

            if feed.bozo and feed.bozo_exception:
                raise FetchError(
                    self.info.name,
                    f"RSS parsing error: {feed.bozo_exception}",
                )

            articles: list[RawArticle] = []

            for entry in feed.entries:
                # Parse publication date
                published_at = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published_at = datetime(*entry.updated_parsed[:6], tzinfo=ZoneInfo("UTC"))

                # Filter by date if specified
                if since and published_at:
                    # Ensure both datetimes are timezone-aware for comparison
                    since_aware = since if since.tzinfo else since.replace(tzinfo=ZoneInfo("UTC"))
                    if published_at < since_aware:
                        continue

                # Extract categories/tags
                categories = []
                if hasattr(entry, "tags"):
                    categories = [tag.term for tag in entry.tags if hasattr(tag, "term")]

                # Create article
                article = RawArticle(
                    external_id=entry.get("id", entry.get("link", "")),
                    primary_source_url=entry.get("link", ""),
                    original_title=entry.get("title", "Untitled"),
                    original_content=entry.get("summary", entry.get("description", "")),
                    published_at=published_at,
                    vendor="AWS",
                    categories=categories,
                    metadata={
                        "source": "aws-whatsnew",
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
        """Check if AWS RSS feed is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(self._feed_url)
                return response.status_code == 200
        except Exception:
            return False
