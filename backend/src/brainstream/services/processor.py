"""Article processing service using LLM for v2."""

import logging
import re
from typing import Optional

from brainstream.llm import BaseLLMProvider, llm_registry
from brainstream.llm.base import ProcessingResult
from brainstream.plugins.base import RawArticle
from brainstream.services.topology import ProcessedArticle

logger = logging.getLogger(__name__)


class ArticleProcessor:
    """Processes raw articles with LLM for v2.

    v2 changes from v1:
    - No personalization (no tech_stack, domains, roles, goals)
    - Adds is_primary_source detection
    - Adds tech_domain classification
    - Outputs ProcessedArticle (for TopologyEngine) instead of SQLAlchemy Article
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self._provider = provider

    async def get_provider(self) -> Optional[BaseLLMProvider]:
        if self._provider:
            return self._provider

        provider = await llm_registry.get_available()
        if provider:
            self._provider = provider
            logger.info(f"Using LLM provider: {provider.display_name}")
        return provider

    async def process_raw_article(
        self,
        raw: RawArticle,
        source_plugin: str = "",
    ) -> ProcessedArticle:
        """Process a raw article with LLM.

        Returns a ProcessedArticle ready for TopologyEngine embedding.
        """
        provider = await self.get_provider()

        # Default values
        summary = ""
        tags = list(raw.categories)
        is_primary_source = False
        tech_domain = ""

        if provider:
            try:
                result = await provider.process_article(
                    title=raw.original_title,
                    content=raw.original_content,
                    url=raw.primary_source_url,
                    vendor=raw.vendor,
                )
                summary = result.summary
                tags = list(set(tags + result.tags))
                is_primary_source = result.is_primary_source
                tech_domain = result.tech_domain
            except Exception as e:
                logger.warning(f"LLM processing failed for {raw.external_id}: {e}")
                summary = self._fallback_summary(raw)
        else:
            logger.info("No LLM provider available, using fallback")
            summary = self._fallback_summary(raw)

        published_at = ""
        if raw.published_at:
            published_at = raw.published_at.isoformat()

        return ProcessedArticle(
            external_id=raw.external_id,
            url=raw.primary_source_url,
            original_title=raw.original_title,
            summary=summary,
            tags=tags,
            vendor=raw.vendor,
            is_primary_source=is_primary_source,
            tech_domain=tech_domain,
            published_at=published_at,
            source_plugin=source_plugin,
        )

    def _fallback_summary(self, raw: RawArticle) -> str:
        """Generate a basic summary when LLM is unavailable."""
        clean_content = re.sub(r"<[^>]+>", "", raw.original_content)
        if len(clean_content) > 300:
            cut = clean_content[:300]
            last_period = cut.rfind(".")
            if last_period > 100:
                clean_content = cut[: last_period + 1]
            else:
                clean_content = cut.rstrip() + "..."
        return clean_content

    async def process_batch(
        self,
        raw_articles: list[RawArticle],
        source_plugin: str = "",
    ) -> list[ProcessedArticle]:
        """Process multiple articles sequentially."""
        results = []
        for raw in raw_articles:
            try:
                article = await self.process_raw_article(raw, source_plugin)
                results.append(article)
                logger.debug(f"Processed: {raw.original_title[:50]}...")
            except Exception as e:
                logger.error(f"Failed to process {raw.external_id}: {e}")
                # Create minimal fallback
                results.append(ProcessedArticle(
                    external_id=raw.external_id,
                    url=raw.primary_source_url,
                    original_title=raw.original_title,
                    summary=raw.original_title,
                    tags=list(raw.categories),
                    vendor=raw.vendor,
                    is_primary_source=False,
                    tech_domain="",
                    published_at=raw.published_at.isoformat() if raw.published_at else "",
                    source_plugin=source_plugin,
                ))
        return results
