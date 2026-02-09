"""FeedSelector: Thompson Sampling based feed generation."""

import logging
from typing import Optional

import numpy as np

from brainstream.core.config import settings
from brainstream.core.database import (
    get_all_cluster_arms,
    log_action,
    update_arm_reward,
    upsert_cluster_arm,
)
from brainstream.models.state import FeedItem
from brainstream.services.topology import TopologyEngine

logger = logging.getLogger(__name__)


class FeedSelector:
    """Generates feeds using Thompson Sampling over topic clusters.

    Algorithm:
    1. Sample from Beta(alpha, beta) for each cluster arm
    2. Select clusters proportional to sampled values
    3. Fill most slots with articles from high-sample clusters
    4. Reserve last slots for boundary articles (serendipity)

    This implements the Phase 1 exploration strategy:
    - No personalization needed
    - Beta(1,1) priors = uniform distribution = maximum exploration initially
    - User actions (click/bookmark) update the arms
    - Naturally converges to exploit good clusters while continuing to explore
    """

    def __init__(self):
        self._topology = TopologyEngine()

    def generate_feed(
        self,
        limit: int = 0,
        vendor_filter: Optional[str] = None,
        primary_only: bool = False,
        offset: int = 0,
    ) -> list[FeedItem]:
        """Generate a feed using Thompson Sampling.

        Args:
            limit: Max number of items (0 = use config default).
            vendor_filter: Optional vendor name to filter.
            primary_only: If True, only show primary source articles.
            offset: Number of items to skip (for pagination).

        Returns:
            List of FeedItems ordered by Thompson Sampling selection.
        """
        if limit <= 0:
            limit = settings.feed_default_limit

        serendipity_slots = settings.serendipity_slots

        # Get cluster arms
        arms = get_all_cluster_arms()

        if not arms:
            # No clusters yet - return latest articles
            return self._get_latest_articles(limit, vendor_filter, primary_only, offset)

        # Thompson Sampling: sample from Beta distribution for each arm
        sampled_values = {}
        for arm in arms:
            cid = arm["cluster_id"]
            alpha = arm.get("alpha", 1.0)
            beta = arm.get("beta", 1.0)
            sampled_values[cid] = float(np.random.beta(alpha, beta))

        # Sort clusters by sampled value (descending)
        sorted_clusters = sorted(sampled_values.items(), key=lambda x: -x[1])

        feed_items: list[FeedItem] = []
        main_slots = limit - serendipity_slots

        # Fill main slots from high-value clusters
        articles_per_cluster = max(1, main_slots // max(len(sorted_clusters), 1))
        remaining_main = main_slots

        for cluster_id, sampled_val in sorted_clusters:
            if remaining_main <= 0:
                break

            n_from_cluster = min(articles_per_cluster, remaining_main)
            articles = self._topology.get_cluster_articles(
                cluster_id, n=n_from_cluster + offset
            )

            # Apply filters and offset
            filtered = self._filter_articles(articles, vendor_filter, primary_only)
            for article in filtered[offset:offset + n_from_cluster]:
                feed_items.append(self._article_to_feed_item(article))
                remaining_main -= 1
                if remaining_main <= 0:
                    break

        # Fill serendipity slots with boundary articles from low-value clusters
        if serendipity_slots > 0 and len(sorted_clusters) > 1:
            # Pick from least-explored clusters (lowest sampled values)
            low_clusters = sorted_clusters[-max(3, len(sorted_clusters) // 2) :]
            seen_ids = {item.id for item in feed_items}

            for cluster_id, _ in low_clusters:
                if serendipity_slots <= 0:
                    break

                boundary = self._topology.get_boundary_articles(cluster_id, n=3)
                filtered = self._filter_articles(boundary, vendor_filter, primary_only)

                for article in filtered:
                    if article["id"] not in seen_ids:
                        feed_items.append(self._article_to_feed_item(article))
                        seen_ids.add(article["id"])
                        serendipity_slots -= 1
                        if serendipity_slots <= 0:
                            break

        return feed_items[:limit]

    def record_action(self, article_id: str, action: str) -> None:
        """Record a user action and update Thompson Sampling arms.

        Args:
            article_id: The article ID.
            action: Action type ('click', 'bookmark', 'skip').
        """
        # Look up the article's cluster
        article = self._topology.get_article(article_id)
        if not article:
            logger.warning(f"Article not found: {article_id}")
            return

        cluster_id = article.get("cluster_id", -1)
        if cluster_id == -1:
            logger.debug(f"Article {article_id} is noise (no cluster)")
            return

        # Log the action
        log_action(article_id, action, cluster_id)

        # Update Thompson Sampling arm
        success = action in ("click", "bookmark")
        update_arm_reward(cluster_id, success)

        logger.info(
            f"Recorded action '{action}' for article {article_id} "
            f"(cluster {cluster_id}, {'success' if success else 'failure'})"
        )

    def _get_latest_articles(
        self,
        limit: int,
        vendor_filter: Optional[str],
        primary_only: bool,
        offset: int,
    ) -> list[FeedItem]:
        """Fallback: get latest articles when no clusters exist."""
        from brainstream.services.topology import get_articles_collection

        collection = get_articles_collection()
        all_data = collection.get(include=["metadatas"])

        if not all_data["ids"]:
            return []

        articles = [
            {"id": all_data["ids"][i], **all_data["metadatas"][i]}
            for i in range(len(all_data["ids"]))
        ]

        # Sort by published date
        articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)

        # Apply filters
        filtered = self._filter_articles(articles, vendor_filter, primary_only)

        return [
            self._article_to_feed_item(a) for a in filtered[offset : offset + limit]
        ]

    def _filter_articles(
        self,
        articles: list[dict],
        vendor_filter: Optional[str],
        primary_only: bool,
    ) -> list[dict]:
        """Apply vendor and primary source filters."""
        result = articles

        if vendor_filter:
            result = [
                a for a in result
                if a.get("vendor", "").lower() == vendor_filter.lower()
            ]

        if primary_only:
            result = [a for a in result if a.get("is_primary_source", False)]

        return result

    def _article_to_feed_item(self, article: dict) -> FeedItem:
        """Convert a ChromaDB article dict to a FeedItem."""
        tags_str = article.get("tags", "")
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        return FeedItem(
            id=article.get("id", ""),
            url=article.get("url", ""),
            title=article.get("original_title", ""),
            summary=article.get("summary", ""),
            tags=tags,
            vendor=article.get("vendor", ""),
            is_primary_source=bool(article.get("is_primary_source", False)),
            cluster_id=article.get("cluster_id", -1),
            published_at=article.get("published_at", ""),
            collected_at=article.get("collected_at", ""),
            source_plugin=article.get("source_plugin", ""),
        )
