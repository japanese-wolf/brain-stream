"""GitHub Releases plugin using GitHub API."""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import httpx

from brainstream.plugins.base import (
    BaseSourcePlugin,
    FetchError,
    PluginInfo,
    RawArticle,
    SourceType,
)

# Default repositories to track (popular developer tools and frameworks)
DEFAULT_REPOSITORIES = [
    # LLM/AI
    "langchain-ai/langchain",
    "openai/openai-python",
    "anthropics/anthropic-sdk-python",
    # Infrastructure
    "hashicorp/terraform",
    "kubernetes/kubernetes",
    "docker/compose",
    # Frameworks
    "tiangolo/fastapi",
    "vercel/next.js",
    "vitejs/vite",
]

GITHUB_API_BASE = "https://api.github.com"


class GitHubReleasesPlugin(BaseSourcePlugin):
    """Plugin for fetching GitHub Releases via API.

    This plugin fetches releases from specified GitHub repositories,
    which is useful for tracking:
    - Framework updates
    - Library releases
    - Tool version changes
    - SDK updates
    """

    def __init__(
        self,
        repositories: Optional[list[str]] = None,
        github_token: Optional[str] = None,
    ) -> None:
        """Initialize the plugin.

        Args:
            repositories: List of repos in "owner/repo" format.
            github_token: Optional GitHub token for higher rate limits.
        """
        self._repositories = repositories or DEFAULT_REPOSITORIES
        self._github_token = github_token

    @property
    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="github-releases",
            display_name="GitHub OSS Releases",
            vendor="GitHub OSS",
            description="Fetches releases from open source GitHub repositories via API",
            source_type=SourceType.API,
            version="1.0.0",
            supported_tech_stack=[
                "langchain", "terraform", "kubernetes", "docker",
                "fastapi", "nextjs", "vite", "react", "python",
            ],
        )

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        return len(self._repositories) > 0

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "BrainStream/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._github_token:
            headers["Authorization"] = f"Bearer {self._github_token}"
        return headers

    def _parse_datetime(self, dt_str: str) -> Optional[datetime]:
        """Parse GitHub datetime string."""
        try:
            # GitHub uses ISO 8601 format: 2024-01-15T12:00:00Z
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return dt.replace(tzinfo=ZoneInfo("UTC"))
        except (ValueError, AttributeError):
            return None

    async def _fetch_repo_releases(
        self,
        client: httpx.AsyncClient,
        repo: str,
        since: Optional[datetime] = None,
    ) -> list[RawArticle]:
        """Fetch releases for a single repository."""
        articles = []

        try:
            url = f"{GITHUB_API_BASE}/repos/{repo}/releases"
            params = {"per_page": 10}  # Limit to recent releases

            response = await client.get(url, params=params, headers=self._get_headers())

            if response.status_code == 404:
                return []  # Repository not found or no releases
            response.raise_for_status()

            releases = response.json()

            for release in releases:
                published_at = self._parse_datetime(release.get("published_at", ""))

                if since and published_at and published_at < since:
                    continue

                # Skip drafts and pre-releases optionally
                if release.get("draft", False):
                    continue

                tag_name = release.get("tag_name", "")
                release_name = release.get("name", tag_name)
                body = release.get("body", "") or ""

                # Create title combining repo and release
                repo_name = repo.split("/")[-1]
                title = f"{repo_name} {release_name}" if release_name else f"{repo_name} {tag_name}"

                # Build content with release notes
                content_parts = []
                if body:
                    content_parts.append(body)

                # Add metadata to content
                if release.get("prerelease"):
                    content_parts.insert(0, "[Pre-release]")

                content = "\n\n".join(content_parts) if content_parts else f"Release {tag_name}"

                # Determine categories based on repo
                categories = ["release", "github"]
                repo_lower = repo.lower()
                if "langchain" in repo_lower:
                    categories.extend(["ai", "llm"])
                elif "openai" in repo_lower or "anthropic" in repo_lower:
                    categories.extend(["ai", "sdk"])
                elif "terraform" in repo_lower:
                    categories.extend(["infrastructure", "iac"])
                elif "kubernetes" in repo_lower or "docker" in repo_lower:
                    categories.extend(["containers", "infrastructure"])
                elif "fastapi" in repo_lower:
                    categories.extend(["python", "api"])
                elif "next" in repo_lower or "vite" in repo_lower:
                    categories.extend(["javascript", "frontend"])

                article = RawArticle(
                    external_id=f"github-{repo}-{release.get('id', tag_name)}",
                    primary_source_url=release.get("html_url", f"https://github.com/{repo}/releases"),
                    original_title=title,
                    original_content=content[:5000],  # Limit content length
                    published_at=published_at,
                    vendor="GitHub OSS",
                    categories=categories,
                    metadata={
                        "source": "github-releases",
                        "repository": repo,
                        "tag_name": tag_name,
                        "prerelease": release.get("prerelease", False),
                    },
                )
                articles.append(article)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                # Rate limit exceeded
                pass
            # Other errors are silently ignored per-repo
        except Exception:
            pass

        return articles

    async def fetch_updates(self, since: Optional[datetime] = None) -> list[RawArticle]:
        """Fetch latest releases from all configured repositories.

        Args:
            since: Optional datetime to filter articles after this date.

        Returns:
            List of RawArticle objects.

        Raises:
            FetchError: If fetching fails completely.
        """
        try:
            all_articles: list[RawArticle] = []

            async with httpx.AsyncClient(timeout=30.0) as client:
                for repo in self._repositories:
                    articles = await self._fetch_repo_releases(client, repo, since)
                    all_articles.extend(articles)

            # Sort by published date (newest first)
            all_articles.sort(
                key=lambda a: a.published_at or datetime.min.replace(tzinfo=ZoneInfo("UTC")),
                reverse=True
            )

            return all_articles

        except Exception as e:
            raise FetchError(self.info.name, f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if GitHub API is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{GITHUB_API_BASE}/rate_limit",
                    headers=self._get_headers()
                )
                return response.status_code == 200
        except Exception:
            return False

    def add_repository(self, repo: str) -> None:
        """Add a repository to track.

        Args:
            repo: Repository in "owner/repo" format.
        """
        if repo not in self._repositories:
            self._repositories.append(repo)

    def remove_repository(self, repo: str) -> None:
        """Remove a repository from tracking.

        Args:
            repo: Repository in "owner/repo" format.
        """
        if repo in self._repositories:
            self._repositories.remove(repo)
