"""Data collection service for v2 - orchestrates plugins, processing, and ChromaDB storage."""

import logging
import time
from dataclasses import dataclass, field

from brainstream.plugins.base import BaseSourcePlugin, RawArticle
from brainstream.plugins.registry import registry as plugin_registry
from brainstream.services.processor import ArticleProcessor
from brainstream.services.topology import TopologyEngine, get_articles_collection

logger = logging.getLogger(__name__)


@dataclass
class CollectionResult:
    """Result of a collection run for one source."""

    source_name: str
    fetched: int
    new: int
    processed: int
    errors: list[str] = field(default_factory=list)
    duration_ms: int = 0


@dataclass
class CollectionSummary:
    """Summary of collection across all sources."""

    total_fetched: int
    total_new: int
    total_processed: int
    sources: list[CollectionResult]
    duration_ms: int


class CollectorService:
    """Collects articles from all sources, processes with LLM, and stores in ChromaDB.

    v2 changes:
    - No SQLAlchemy / async sessions
    - ChromaDB as primary storage (via TopologyEngine)
    - No tech_stack / personalization
    - Automatic re-clustering after collection
    """

    def __init__(self, skip_processing: bool = False):
        self._skip_processing = skip_processing
        self._processor = ArticleProcessor()
        self._topology = TopologyEngine()

    async def collect_all(self) -> CollectionSummary:
        """Collect from all enabled sources."""
        start = time.time()
        results: list[CollectionResult] = []
        total_fetched = 0
        total_new = 0
        total_processed = 0

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
                ))

        # Re-cluster after all collections
        if total_new > 0:
            logger.info("Re-clustering after new articles...")
            self._topology.recluster()

        return CollectionSummary(
            total_fetched=total_fetched,
            total_new=total_new,
            total_processed=total_processed,
            sources=results,
            duration_ms=int((time.time() - start) * 1000),
        )

    async def collect_from_plugin(self, plugin: BaseSourcePlugin) -> CollectionResult:
        """Collect from a specific plugin."""
        start = time.time()
        plugin_name = plugin.info.name

        logger.info(f"Collecting from {plugin_name}...")

        # Fetch raw articles
        try:
            raw_articles = await plugin.fetch_updates()
            logger.info(f"Fetched {len(raw_articles)} articles from {plugin_name}")
        except Exception as e:
            logger.error(f"Fetch failed for {plugin_name}: {e}")
            raise

        # Deduplicate against ChromaDB
        new_articles = self._deduplicate(raw_articles)
        logger.info(f"Found {len(new_articles)} new articles from {plugin_name}")

        if not new_articles:
            return CollectionResult(
                source_name=plugin_name,
                fetched=len(raw_articles),
                new=0,
                processed=0,
                duration_ms=int((time.time() - start) * 1000),
            )

        # Process with LLM
        processed_count = 0
        if not self._skip_processing:
            processed_articles = await self._processor.process_batch(
                new_articles,
                source_plugin=plugin_name,
            )
            # Store in ChromaDB via TopologyEngine
            stored = self._topology.embed_and_store(processed_articles)
            processed_count = stored
        else:
            # Store without LLM processing (minimal metadata)
            from brainstream.services.topology import ProcessedArticle

            minimal = [
                ProcessedArticle(
                    external_id=r.external_id,
                    url=r.primary_source_url,
                    original_title=r.original_title,
                    summary=r.original_title,
                    tags=list(r.categories),
                    vendor=r.vendor,
                    is_primary_source=False,
                    tech_domain="",
                    published_at=r.published_at.isoformat() if r.published_at else "",
                    source_plugin=plugin_name,
                )
                for r in new_articles
            ]
            stored = self._topology.embed_and_store(minimal)
            processed_count = stored

        return CollectionResult(
            source_name=plugin_name,
            fetched=len(raw_articles),
            new=len(new_articles),
            processed=processed_count,
            duration_ms=int((time.time() - start) * 1000),
        )

    def _deduplicate(self, raw_articles: list[RawArticle]) -> list[RawArticle]:
        """Filter out articles that already exist in ChromaDB."""
        if not raw_articles:
            return []

        collection = get_articles_collection()
        external_ids = [a.external_id for a in raw_articles]

        existing_ids = set()
        try:
            result = collection.get(ids=external_ids)
            existing_ids = set(result["ids"])
        except Exception:
            pass

        return [a for a in raw_articles if a.external_id not in existing_ids]


# Convenience functions
async def collect_all(skip_processing: bool = False) -> CollectionSummary:
    """Collect from all sources."""
    collector = CollectorService(skip_processing=skip_processing)
    return await collector.collect_all()


async def collect_from_source(
    source_name: str, skip_processing: bool = False
) -> CollectionResult:
    """Collect from a specific source."""
    plugin = plugin_registry.get(source_name)
    if not plugin:
        raise ValueError(f"Source not found: {source_name}")

    collector = CollectorService(skip_processing=skip_processing)
    return await collector.collect_from_plugin(plugin)
