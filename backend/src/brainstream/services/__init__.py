"""Business logic services for BrainStream."""

from brainstream.services.collector import (
    CollectionResult,
    CollectionSummary,
    CollectorService,
    collect_all,
    collect_from_source,
)
from brainstream.services.processor import ArticleProcessor, process_article
from brainstream.services.relevance import (
    RelevanceScore,
    RelevanceService,
    calculate_relevance,
)

__all__ = [
    "ArticleProcessor",
    "CollectorService",
    "CollectionResult",
    "CollectionSummary",
    "RelevanceScore",
    "RelevanceService",
    "calculate_relevance",
    "collect_all",
    "collect_from_source",
    "process_article",
]
