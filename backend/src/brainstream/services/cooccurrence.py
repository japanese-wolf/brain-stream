"""Tag co-occurrence analysis for discovering trending technologies."""

from collections import defaultdict
from dataclasses import dataclass, field

from brainstream.models.article import Article


@dataclass
class TrendingTechnology:
    """A technology trending in the user's field."""

    name: str
    count: int
    related_to: list[str] = field(default_factory=list)
    sample_article_ids: list[str] = field(default_factory=list)


class CoOccurrenceService:
    """Analyzes tag co-occurrence to find technologies trending near the user's stack.

    Direction A (known -> unknown): Identifies technologies that frequently
    co-occur with the user's tech stack tags but are not in the stack itself.
    No LLM required — accuracy improves as more articles accumulate.
    """

    def __init__(self, tech_stack: list[str], max_results: int = 10):
        self._tech_stack = {t.lower() for t in tech_stack}
        self._max_results = max_results

    def analyze(self, articles: list[Article]) -> list[TrendingTechnology]:
        """Analyze articles to find trending technologies.

        Args:
            articles: All articles to analyze.

        Returns:
            List of trending technologies sorted by co-occurrence count.
        """
        if not self._tech_stack or not articles:
            return []

        # tag -> {related_tech_stack_tags, count, article_ids}
        outside_tags: dict[str, dict] = defaultdict(
            lambda: {"related_to": set(), "count": 0, "article_ids": []}
        )

        for article in articles:
            if not article.tags:
                continue

            normalized_tags = set()
            for tag in article.tags:
                normalized = self._normalize_tag(tag)
                if normalized:
                    normalized_tags.add(normalized)

            # Find which tech_stack tags appear in this article
            stack_hits = normalized_tags & self._tech_stack
            if not stack_hits:
                continue

            # Find tags outside the tech stack
            outside = normalized_tags - self._tech_stack
            for tag in outside:
                entry = outside_tags[tag]
                entry["related_to"].update(stack_hits)
                entry["count"] += 1
                if len(entry["article_ids"]) < 3:
                    entry["article_ids"].append(article.id)

        # Sort by count descending, take top N
        sorted_tags = sorted(
            outside_tags.items(), key=lambda x: x[1]["count"], reverse=True
        )

        return [
            TrendingTechnology(
                name=tag,
                count=data["count"],
                related_to=sorted(data["related_to"]),
                sample_article_ids=data["article_ids"],
            )
            for tag, data in sorted_tags[: self._max_results]
            if data["count"] >= 2  # Require at least 2 co-occurrences
        ]

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        """Normalize a tag for comparison."""
        tag = tag.lower().strip()
        # Remove common prefixes from structured tags (e.g. "category:aws")
        if ":" in tag:
            tag = tag.split(":")[-1].strip()
        # Remove commas (tags sometimes have "tag1,tag2" format)
        if "," in tag:
            tag = tag.split(",")[0].strip()
        return tag
