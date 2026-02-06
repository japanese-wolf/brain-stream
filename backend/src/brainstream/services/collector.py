"""Data collection service orchestrating plugins, processing, and storage."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from brainstream.core.database import get_session
from brainstream.models.article import Article, DataSource
from brainstream.plugins.base import BaseSourcePlugin, RawArticle
from brainstream.plugins.registry import registry as plugin_registry
from brainstream.services.processor import ArticleProcessor

logger = logging.getLogger(__name__)


@dataclass
class CollectionResult:
    """Result of a collection run."""

    source_name: str
    fetched: int
    new: int
    processed: int
    errors: list[str]
    duration_ms: int


@dataclass
class CollectionSummary:
    """Summary of collection across all sources."""

    total_fetched: int
    total_new: int
    total_processed: int
    sources: list[CollectionResult]
    duration_ms: int


class CollectorService:
    """Service for collecting and processing articles from all sources.

    Orchestrates:
    1. Plugin data fetching
    2. Deduplication
    3. LLM processing
    4. Database storage
    """

    def __init__(
        self,
        tech_stack: Optional[list[str]] = None,
        skip_processing: bool = False,
    ):
        """Initialize the collector.

        Args:
            tech_stack: User's tech stack for relevance analysis.
            skip_processing: If True, skip LLM processing (for testing).
        """
        self._tech_stack = tech_stack or []
        self._skip_processing = skip_processing
        self._processor = ArticleProcessor(tech_stack=tech_stack)

    async def collect_all(self) -> CollectionSummary:
        """Collect from all enabled sources.

        Returns:
            CollectionSummary with results from all sources.
        """
        import time

        start_time = time.time()
        results: list[CollectionResult] = []
        total_fetched = 0
        total_new = 0
        total_processed = 0

        # Get all plugins
        plugins = plugin_registry.get_all()

        for plugin in plugins:
            try:
                result = await self.collect_from_plugin(plugin)
                results.append(result)
                total_fetched += result.fetched
                total_new += result.new
                total_processed += result.processed
            except Exception as e:
                logger.error(f"Collection failed for {plugin.info.name}: {e}")
                results.append(CollectionResult(
                    source_name=plugin.info.name,
                    fetched=0,
                    new=0,
                    processed=0,
                    errors=[str(e)],
                    duration_ms=0,
                ))

        duration_ms = int((time.time() - start_time) * 1000)

        return CollectionSummary(
            total_fetched=total_fetched,
            total_new=total_new,
            total_processed=total_processed,
            sources=results,
            duration_ms=duration_ms,
        )

    async def collect_from_plugin(
        self,
        plugin: BaseSourcePlugin,
    ) -> CollectionResult:
        """Collect from a specific plugin.

        Args:
            plugin: Plugin instance to collect from.

        Returns:
            CollectionResult for this source.
        """
        import time

        start_time = time.time()
        errors: list[str] = []
        plugin_name = plugin.info.name

        logger.info(f"Collecting from {plugin_name}...")

        async with get_session() as session:
            # Get or create data source record
            source = await self._get_or_create_source(session, plugin)

            # Fetch raw articles
            try:
                raw_articles = await plugin.fetch_updates(since=source.last_fetched_at)
                logger.info(f"Fetched {len(raw_articles)} articles from {plugin_name}")
            except Exception as e:
                logger.error(f"Fetch failed for {plugin_name}: {e}")
                source.fetch_status = "error"
                source.error_message = str(e)
                await session.commit()
                raise

            # Deduplicate
            new_articles = await self._deduplicate(session, raw_articles)
            logger.info(f"Found {len(new_articles)} new articles")

            # Process with LLM
            processed_count = 0
            if not self._skip_processing and new_articles:
                processed_articles = await self._processor.process_batch(
                    new_articles,
                    source_id=source.id,
                )

                # Save to database
                for article in processed_articles:
                    session.add(article)
                    if article.processed_at:
                        processed_count += 1

                await session.commit()
                logger.info(f"Saved {len(processed_articles)} articles")
            elif new_articles:
                # Save without processing
                for raw in new_articles:
                    article = Article(
                        source_id=source.id,
                        external_id=raw.external_id,
                        primary_source_url=raw.primary_source_url,
                        original_title=raw.original_title,
                        original_content=raw.original_content,
                        vendor=raw.vendor,
                        published_at=raw.published_at,
                        tags=raw.categories,
                    )
                    session.add(article)
                await session.commit()

            # Update source status
            source.last_fetched_at = datetime.now(UTC)
            source.fetch_status = "healthy"
            source.error_message = None
            await session.commit()

        duration_ms = int((time.time() - start_time) * 1000)

        return CollectionResult(
            source_name=plugin_name,
            fetched=len(raw_articles),
            new=len(new_articles),
            processed=processed_count,
            errors=errors,
            duration_ms=duration_ms,
        )

    async def _get_or_create_source(
        self,
        session: AsyncSession,
        plugin: BaseSourcePlugin,
    ) -> DataSource:
        """Get or create a data source record for a plugin."""
        info = plugin.info

        query = select(DataSource).where(DataSource.plugin_name == info.name)
        result = await session.execute(query)
        source = result.scalar_one_or_none()

        if not source:
            source = DataSource(
                plugin_name=info.name,
                name=info.display_name,
                vendor=info.vendor,
                enabled=True,
                config={},
            )
            session.add(source)
            await session.commit()
            await session.refresh(source)
        else:
            # Update vendor/display_name if plugin definition changed
            if source.vendor != info.vendor or source.name != info.display_name:
                old_vendor = source.vendor
                source.vendor = info.vendor
                source.name = info.display_name
                # Also update vendor on existing articles for this source
                if old_vendor != info.vendor:
                    await session.execute(
                        update(Article)
                        .where(Article.source_id == source.id)
                        .values(vendor=info.vendor)
                    )
                    logger.info(
                        f"Updated vendor for source {info.name}: "
                        f"{old_vendor} -> {info.vendor}"
                    )
                await session.commit()

        return source

    async def _deduplicate(
        self,
        session: AsyncSession,
        raw_articles: list[RawArticle],
    ) -> list[RawArticle]:
        """Filter out articles that already exist in database.

        Args:
            session: Database session.
            raw_articles: List of raw articles.

        Returns:
            List of articles not yet in database.
        """
        if not raw_articles:
            return []

        # Get external IDs
        external_ids = [a.external_id for a in raw_articles]

        # Check which ones exist
        query = select(Article.external_id).where(Article.external_id.in_(external_ids))
        result = await session.execute(query)
        existing_ids = set(row[0] for row in result.fetchall())

        # Filter to new articles only
        new_articles = [a for a in raw_articles if a.external_id not in existing_ids]

        return new_articles


@dataclass
class ProcessingResult:
    """Result of processing unprocessed articles."""

    total: int
    processed: int
    failed: int


async def process_unprocessed(
    tech_stack: Optional[list[str]] = None,
    limit: int = 50,
) -> "ProcessingResult":
    """Process existing unprocessed articles with LLM.

    Args:
        tech_stack: User's tech stack for relevance analysis.
        limit: Max number of articles to process in one batch.

    Returns:
        ProcessingResult with counts.
    """
    processor = ArticleProcessor(tech_stack=tech_stack)

    async with get_session() as session:
        # Find unprocessed articles
        query = (
            select(Article)
            .where(Article.processed_at.is_(None))
            .order_by(Article.collected_at.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        articles = result.scalars().all()

        total = len(articles)
        processed = 0
        failed = 0

        for article in articles:
            success = await processor.process_existing_article(article)
            if success:
                processed += 1
            else:
                failed += 1

        await session.commit()

    return ProcessingResult(total=total, processed=processed, failed=failed)


# Convenience functions
async def collect_all(
    tech_stack: Optional[list[str]] = None,
    skip_processing: bool = False,
) -> CollectionSummary:
    """Collect from all sources.

    Args:
        tech_stack: User's tech stack for relevance analysis.
        skip_processing: Skip LLM processing.

    Returns:
        CollectionSummary.
    """
    collector = CollectorService(
        tech_stack=tech_stack,
        skip_processing=skip_processing,
    )
    return await collector.collect_all()


async def collect_from_source(
    source_name: str,
    tech_stack: Optional[list[str]] = None,
    skip_processing: bool = False,
) -> CollectionResult:
    """Collect from a specific source.

    Args:
        source_name: Plugin name (e.g., 'aws-whatsnew').
        tech_stack: User's tech stack.
        skip_processing: Skip LLM processing.

    Returns:
        CollectionResult.

    Raises:
        ValueError: If source not found.
    """
    plugin = plugin_registry.get(source_name)
    if not plugin:
        raise ValueError(f"Source not found: {source_name}")

    collector = CollectorService(
        tech_stack=tech_stack,
        skip_processing=skip_processing,
    )
    return await collector.collect_from_plugin(plugin)
