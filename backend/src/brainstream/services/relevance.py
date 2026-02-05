"""Relevance scoring service for articles based on user tech stack."""

import re
from dataclasses import dataclass
from typing import Optional

from brainstream.models.article import Article


@dataclass
class RelevanceScore:
    """Relevance score breakdown for an article."""

    total_score: float
    """Overall relevance score (0.0 to 1.0)."""

    tag_score: float
    """Score from matching tags (0.0 to 1.0)."""

    vendor_score: float
    """Score from matching preferred vendors (0.0 to 1.0)."""

    content_score: float
    """Score from keyword matches in content (0.0 to 1.0)."""

    matched_tags: list[str]
    """Tags that matched the user's tech stack."""

    matched_keywords: list[str]
    """Keywords found in content that matched tech stack."""

    @property
    def relevance_level(self) -> str:
        """Get human-readable relevance level."""
        if self.total_score >= 0.7:
            return "high"
        elif self.total_score >= 0.4:
            return "medium"
        elif self.total_score > 0:
            return "low"
        return "none"


class RelevanceService:
    """Service for calculating article relevance to a user's tech stack.

    The relevance score is calculated based on:
    1. Tag matching (40% weight): Direct matches between article tags and tech stack
    2. Vendor matching (30% weight): Whether the article's vendor is in preferred vendors
    3. Content matching (30% weight): Keyword occurrences in title/content

    Scores range from 0.0 (no relevance) to 1.0 (highly relevant).
    """

    # Weights for different scoring components
    TAG_WEIGHT = 0.4
    VENDOR_WEIGHT = 0.3
    CONTENT_WEIGHT = 0.3

    def __init__(
        self,
        tech_stack: Optional[list[str]] = None,
        preferred_vendors: Optional[list[str]] = None,
    ):
        """Initialize the relevance service.

        Args:
            tech_stack: User's tech stack (e.g., ["lambda", "ec2", "kubernetes"]).
            preferred_vendors: Preferred vendor names (e.g., ["AWS", "GCP"]).
        """
        self._tech_stack = [t.lower() for t in (tech_stack or [])]
        self._preferred_vendors = [v.lower() for v in (preferred_vendors or [])]

        # Build regex patterns for efficient content matching
        if self._tech_stack:
            # Create word boundary pattern for each tech
            patterns = [rf"\b{re.escape(tech)}\b" for tech in self._tech_stack]
            self._content_pattern = re.compile("|".join(patterns), re.IGNORECASE)
        else:
            self._content_pattern = None

    def calculate_score(self, article: Article) -> RelevanceScore:
        """Calculate relevance score for an article.

        Args:
            article: Article to score.

        Returns:
            RelevanceScore with detailed breakdown.
        """
        # If no tech stack is set, return neutral score
        if not self._tech_stack and not self._preferred_vendors:
            return RelevanceScore(
                total_score=0.5,  # Neutral
                tag_score=0.0,
                vendor_score=0.0,
                content_score=0.0,
                matched_tags=[],
                matched_keywords=[],
            )

        # Calculate tag score
        tag_score, matched_tags = self._calculate_tag_score(article)

        # Calculate vendor score
        vendor_score = self._calculate_vendor_score(article)

        # Calculate content score
        content_score, matched_keywords = self._calculate_content_score(article)

        # Combine scores with weights
        total_score = (
            tag_score * self.TAG_WEIGHT
            + vendor_score * self.VENDOR_WEIGHT
            + content_score * self.CONTENT_WEIGHT
        )

        # Boost score if there are direct tag matches
        if matched_tags:
            total_score = min(1.0, total_score + 0.1 * len(matched_tags))

        return RelevanceScore(
            total_score=round(total_score, 3),
            tag_score=round(tag_score, 3),
            vendor_score=round(vendor_score, 3),
            content_score=round(content_score, 3),
            matched_tags=matched_tags,
            matched_keywords=matched_keywords,
        )

    def _calculate_tag_score(self, article: Article) -> tuple[float, list[str]]:
        """Calculate score based on tag matching."""
        if not self._tech_stack or not article.tags:
            return 0.0, []

        article_tags = [t.lower() for t in article.tags]
        matched_tags = []

        for tech in self._tech_stack:
            for tag in article_tags:
                if tech in tag or tag in tech:
                    matched_tags.append(tag)

        if not matched_tags:
            return 0.0, []

        # Score based on number of matches relative to tech stack size
        score = min(1.0, len(matched_tags) / len(self._tech_stack))
        return score, list(set(matched_tags))

    def _calculate_vendor_score(self, article: Article) -> float:
        """Calculate score based on vendor preference."""
        if not self._preferred_vendors or not article.vendor:
            return 0.0

        article_vendor = article.vendor.lower()
        if article_vendor in self._preferred_vendors:
            return 1.0

        # Partial match for vendor names
        for vendor in self._preferred_vendors:
            if vendor in article_vendor or article_vendor in vendor:
                return 0.8

        return 0.0

    def _calculate_content_score(self, article: Article) -> tuple[float, list[str]]:
        """Calculate score based on content keyword matching."""
        if not self._content_pattern:
            return 0.0, []

        # Combine title and content for searching
        text = f"{article.original_title} {article.original_content}"
        if article.summary_title:
            text += f" {article.summary_title}"
        if article.summary_content:
            text += f" {article.summary_content}"

        matches = self._content_pattern.findall(text.lower())
        if not matches:
            return 0.0, []

        # Unique matches
        unique_matches = list(set(matches))

        # Score based on number of unique keyword matches
        score = min(1.0, len(unique_matches) / max(3, len(self._tech_stack)))
        return score, unique_matches

    def filter_articles(
        self,
        articles: list[Article],
        min_score: float = 0.0,
    ) -> list[tuple[Article, RelevanceScore]]:
        """Filter and score multiple articles.

        Args:
            articles: List of articles to filter.
            min_score: Minimum relevance score to include (0.0 to 1.0).

        Returns:
            List of (article, score) tuples sorted by relevance (highest first).
        """
        scored_articles = []

        for article in articles:
            score = self.calculate_score(article)
            if score.total_score >= min_score:
                scored_articles.append((article, score))

        # Sort by total score descending
        scored_articles.sort(key=lambda x: x[1].total_score, reverse=True)
        return scored_articles

    def prioritize_feed(
        self,
        articles: list[Article],
        high_relevance_first: bool = True,
    ) -> list[tuple[Article, RelevanceScore]]:
        """Prioritize articles for feed display.

        High relevance articles appear first, followed by medium, then low.
        Within each group, articles are sorted by published date (newest first).

        Args:
            articles: List of articles to prioritize.
            high_relevance_first: If True, sort by relevance then date.
                                  If False, sort by date with relevance as secondary.

        Returns:
            List of (article, score) tuples in prioritized order.
        """
        scored = [(article, self.calculate_score(article)) for article in articles]

        if high_relevance_first:
            # Primary: relevance score (descending)
            # Secondary: published date (descending, newest first)
            scored.sort(
                key=lambda x: (
                    x[1].total_score,
                    x[0].published_at.timestamp() if x[0].published_at else 0,
                ),
                reverse=True,
            )
        else:
            # Primary: published date (descending)
            # Secondary: relevance score (descending)
            scored.sort(
                key=lambda x: (
                    x[0].published_at.timestamp() if x[0].published_at else 0,
                    x[1].total_score,
                ),
                reverse=True,
            )

        return scored


def calculate_relevance(
    article: Article,
    tech_stack: Optional[list[str]] = None,
    preferred_vendors: Optional[list[str]] = None,
) -> RelevanceScore:
    """Calculate relevance score for a single article.

    Convenience function for one-off scoring.

    Args:
        article: Article to score.
        tech_stack: User's tech stack.
        preferred_vendors: User's preferred vendors.

    Returns:
        RelevanceScore for the article.
    """
    service = RelevanceService(tech_stack=tech_stack, preferred_vendors=preferred_vendors)
    return service.calculate_score(article)
