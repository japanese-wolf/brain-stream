"""Article processing service using LLM."""

import logging
from datetime import UTC, datetime
from typing import Optional

from brainstream.llm import BaseLLMProvider, ProcessingResult, llm_registry
from brainstream.models.article import Article
from brainstream.plugins.base import RawArticle

logger = logging.getLogger(__name__)


class ArticleProcessor:
    """Service for processing articles with LLM.

    Transforms RawArticle (from plugins) into processed Article
    with AI-generated summaries, tags, and relevance scores.
    """

    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        tech_stack: Optional[list[str]] = None,
        domains: Optional[list[str]] = None,
        roles: Optional[list[str]] = None,
        goals: Optional[list[str]] = None,
    ):
        """Initialize the processor.

        Args:
            provider: LLM provider to use. If None, auto-detects available provider.
            tech_stack: User's tech stack for relevance analysis.
            domains: User's domains of expertise/interest.
            roles: User's engineering roles.
            goals: User's current goals.
        """
        self._provider = provider
        self._tech_stack = tech_stack or []
        self._domains = domains or []
        self._roles = roles or []
        self._goals = goals or []

    async def get_provider(self) -> Optional[BaseLLMProvider]:
        """Get the LLM provider, auto-detecting if needed."""
        if self._provider:
            return self._provider

        # Try to get available provider
        provider = await llm_registry.get_available()
        if provider:
            self._provider = provider
            logger.info(f"Using LLM provider: {provider.display_name}")
        return provider

    async def process_raw_article(
        self,
        raw: RawArticle,
        source_id: Optional[str] = None,
    ) -> Article:
        """Process a raw article with LLM.

        Args:
            raw: Raw article from a plugin.
            source_id: Optional data source ID.

        Returns:
            Processed Article model instance.
        """
        provider = await self.get_provider()

        # Create base article
        article = Article(
            source_id=source_id,
            external_id=raw.external_id,
            primary_source_url=raw.primary_source_url,
            original_title=raw.original_title,
            original_content=raw.original_content,
            vendor=raw.vendor,
            published_at=raw.published_at,
            tags=raw.categories,  # Start with original categories
        )

        # Process with LLM if available
        if provider:
            try:
                result = await provider.process_article(
                    title=raw.original_title,
                    content=raw.original_content,
                    vendor=raw.vendor,
                    tech_stack=self._tech_stack if self._tech_stack else None,
                    domains=self._domains if self._domains else None,
                    roles=self._roles if self._roles else None,
                    goals=self._goals if self._goals else None,
                )
                self._apply_processing_result(article, result)
            except Exception as e:
                logger.warning(f"LLM processing failed for {raw.external_id}: {e}")
                self._apply_fallback(article, raw)
        else:
            logger.info("No LLM provider available, applying fallback processing")
            self._apply_fallback(article, raw)

        return article

    def _apply_processing_result(
        self,
        article: Article,
        result: ProcessingResult,
    ) -> None:
        """Apply LLM processing result to article."""
        # Apply summary
        article.summary_title = result.summary.title
        article.summary_content = result.summary.content
        article.diff_description = result.summary.diff_description
        article.explanation = result.summary.explanation

        # Merge tags (original + extracted)
        all_tags = set(article.tags) if article.tags else set()
        all_tags.update(result.tags.tags)
        all_tags.update(result.tags.vendor_services)
        article.tags = list(all_tags)

        # Apply discovery fields (Phase 1: Direction B)
        article.related_technologies = result.summary.related_technologies
        article.tech_stack_connection = result.summary.tech_stack_connection

        # Mark as processed
        article.processed_at = datetime.now(UTC)
        article.llm_provider = result.provider
        article.llm_model = result.model

    def _apply_fallback(self, article: Article, raw: RawArticle) -> None:
        """Apply fallback processing when LLM is unavailable.

        Generates basic summary fields from the original content so that
        the UI can display something meaningful.
        """
        article.summary_title = raw.original_title

        # Strip HTML tags for a cleaner summary
        import re

        clean_content = re.sub(r"<[^>]+>", "", raw.original_content)
        # Truncate to first ~300 chars at a sentence boundary
        if len(clean_content) > 300:
            cut = clean_content[:300]
            last_period = cut.rfind(".")
            if last_period > 100:
                clean_content = cut[: last_period + 1]
            else:
                clean_content = cut.rstrip() + "..."

        article.summary_content = clean_content
        article.processed_at = datetime.now(UTC)
        article.llm_provider = "fallback"

    async def process_existing_article(self, article: Article) -> bool:
        """Process an existing unprocessed Article in-place with LLM.

        Args:
            article: Existing Article from the database.

        Returns:
            True if successfully processed, False otherwise.
        """
        provider = await self.get_provider()
        if not provider:
            logger.info("No LLM provider available, skipping processing")
            return False

        try:
            result = await provider.process_article(
                title=article.original_title,
                content=article.original_content,
                vendor=article.vendor,
                tech_stack=self._tech_stack if self._tech_stack else None,
                domains=self._domains if self._domains else None,
                roles=self._roles if self._roles else None,
                goals=self._goals if self._goals else None,
            )
            self._apply_processing_result(article, result)
            return True
        except Exception as e:
            logger.warning(f"LLM processing failed for {article.external_id}: {e}")
            return False

    async def process_batch(
        self,
        raw_articles: list[RawArticle],
        source_id: Optional[str] = None,
        max_concurrent: int = 1,
    ) -> list[Article]:
        """Process multiple articles.

        Args:
            raw_articles: List of raw articles.
            source_id: Optional data source ID.
            max_concurrent: Maximum concurrent processing (default 1 for sequential).

        Returns:
            List of processed Article instances.
        """
        articles = []

        # Process sequentially for now (to respect rate limits)
        for raw in raw_articles:
            try:
                article = await self.process_raw_article(raw, source_id)
                articles.append(article)
                logger.debug(f"Processed: {raw.original_title[:50]}...")
            except Exception as e:
                logger.error(f"Failed to process {raw.external_id}: {e}")
                # Create unprocessed article as fallback
                articles.append(Article(
                    source_id=source_id,
                    external_id=raw.external_id,
                    primary_source_url=raw.primary_source_url,
                    original_title=raw.original_title,
                    original_content=raw.original_content,
                    vendor=raw.vendor,
                    published_at=raw.published_at,
                    tags=raw.categories,
                ))

        return articles


# Convenience function
async def process_article(
    raw: RawArticle,
    tech_stack: Optional[list[str]] = None,
) -> Article:
    """Process a single raw article.

    Args:
        raw: Raw article from a plugin.
        tech_stack: Optional user's tech stack.

    Returns:
        Processed Article instance.
    """
    processor = ArticleProcessor(tech_stack=tech_stack)
    return await processor.process_raw_article(raw)
