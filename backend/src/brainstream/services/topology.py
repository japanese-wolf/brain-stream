"""TopologyEngine: embedding, clustering, and information space topology."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from brainstream.core.config import settings
from brainstream.core.database import get_all_cluster_arms, upsert_cluster_arm
from brainstream.models.state import ClusterInfo

logger = logging.getLogger(__name__)

# Lazy-loaded globals
_chroma_client: Optional[chromadb.PersistentClient] = None
_embedding_model: Optional[SentenceTransformer] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        settings.ensure_data_dir()
        _chroma_client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_dir)
        )
    return _chroma_client


def get_embedding_model() -> SentenceTransformer:
    """Get or create the sentence-transformers model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model: %s", settings.embedding_model)
        _embedding_model = SentenceTransformer(settings.embedding_model)
    return _embedding_model


def get_articles_collection() -> chromadb.Collection:
    """Get or create the articles collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="articles",
        metadata={"hnsw:space": "cosine"},
    )


@dataclass
class ProcessedArticle:
    """Article with LLM processing results, ready for embedding."""

    external_id: str
    url: str
    original_title: str
    summary: str
    tags: list[str]
    vendor: str
    is_primary_source: bool
    tech_domain: str
    published_at: str
    source_plugin: str


class TopologyEngine:
    """Manages the information space topology.

    Responsibilities:
    1. Generate embeddings for articles
    2. Store articles in ChromaDB
    3. Run HDBSCAN clustering
    4. Calculate cluster densities
    5. Identify boundary articles between clusters
    """

    def __init__(self):
        self._collection = get_articles_collection()
        self._model = get_embedding_model()

    def embed_and_store(self, articles: list[ProcessedArticle]) -> int:
        """Generate embeddings and store articles in ChromaDB.

        Returns the number of articles actually stored (skipping duplicates).
        """
        if not articles:
            return 0

        # Check for existing IDs to skip duplicates
        existing_ids = set()
        try:
            existing = self._collection.get(
                ids=[a.external_id for a in articles],
            )
            existing_ids = set(existing["ids"])
        except Exception:
            pass

        new_articles = [a for a in articles if a.external_id not in existing_ids]
        if not new_articles:
            logger.info("No new articles to embed")
            return 0

        # Generate embeddings
        texts = [f"{a.original_title} {a.summary}" for a in new_articles]
        embeddings = self._model.encode(texts, show_progress_bar=False)

        now = datetime.now(UTC).isoformat()

        # Store in ChromaDB
        self._collection.add(
            ids=[a.external_id for a in new_articles],
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[
                {
                    "url": a.url,
                    "original_title": a.original_title,
                    "summary": a.summary,
                    "tags": ",".join(a.tags),
                    "vendor": a.vendor,
                    "published_at": a.published_at,
                    "is_primary_source": a.is_primary_source,
                    "tech_domain": a.tech_domain,
                    "cluster_id": -1,
                    "collected_at": now,
                    "source_plugin": a.source_plugin,
                }
                for a in new_articles
            ],
        )

        logger.info("Embedded and stored %d new articles", len(new_articles))
        return len(new_articles)

    def recluster(self) -> dict[int, int]:
        """Run HDBSCAN clustering on all articles.

        Returns a dict of cluster_id -> article_count.
        """
        # Get all embeddings from ChromaDB
        all_data = self._collection.get(include=["embeddings", "metadatas"])

        if not all_data["ids"]:
            logger.info("No articles to cluster")
            return {}

        ids = all_data["ids"]
        embeddings = np.array(all_data["embeddings"])

        n_articles = len(ids)
        logger.info("Clustering %d articles", n_articles)

        if n_articles < settings.hdbscan_min_cluster_size:
            # Too few articles for HDBSCAN - assign all to cluster 0
            labels = np.zeros(n_articles, dtype=int)
            logger.info("Too few articles for HDBSCAN, assigning all to cluster 0")
        else:
            import hdbscan

            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=settings.hdbscan_min_cluster_size,
                min_samples=settings.hdbscan_min_samples,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(embeddings)

        # Update cluster_id in ChromaDB metadata
        for i, article_id in enumerate(ids):
            metadata = all_data["metadatas"][i].copy()
            metadata["cluster_id"] = int(labels[i])
            self._collection.update(
                ids=[article_id],
                metadatas=[metadata],
            )

        # Count articles per cluster
        cluster_counts: dict[int, int] = {}
        for label in labels:
            cluster_id = int(label)
            cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1

        # Sync cluster arms in SQLite
        for cluster_id, count in cluster_counts.items():
            if cluster_id == -1:
                continue  # Skip noise
            upsert_cluster_arm(cluster_id=cluster_id, article_count=count)

        logger.info(
            "Clustering complete: %d clusters, %d noise articles",
            len([c for c in cluster_counts if c != -1]),
            cluster_counts.get(-1, 0),
        )

        return cluster_counts

    def get_cluster_density(self) -> dict[int, float]:
        """Calculate relative density for each cluster.

        Returns cluster_id -> density (fraction of total articles).
        """
        all_data = self._collection.get(include=["metadatas"])
        if not all_data["ids"]:
            return {}

        total = len(all_data["ids"])
        counts: dict[int, int] = {}
        for meta in all_data["metadatas"]:
            cid = meta.get("cluster_id", -1)
            counts[cid] = counts.get(cid, 0) + 1

        return {cid: count / total for cid, count in counts.items() if cid != -1}

    def get_cluster_articles(
        self, cluster_id: int, n: int = 10, newest_first: bool = True
    ) -> list[dict]:
        """Get articles from a specific cluster.

        Returns articles sorted by published date (newest first by default).
        """
        all_data = self._collection.get(include=["metadatas"])

        articles = []
        for i, meta in enumerate(all_data["metadatas"]):
            if meta.get("cluster_id") == cluster_id:
                articles.append({
                    "id": all_data["ids"][i],
                    **meta,
                })

        if newest_first:
            articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)

        return articles[:n]

    def get_boundary_articles(self, cluster_id: int, n: int = 3) -> list[dict]:
        """Get articles at the boundary of a cluster (farthest from centroid).

        These are the best candidates for serendipitous discovery.
        """
        all_data = self._collection.get(include=["embeddings", "metadatas"])

        if not all_data["ids"]:
            return []

        # Get articles in this cluster
        cluster_indices = []
        for i, meta in enumerate(all_data["metadatas"]):
            if meta.get("cluster_id") == cluster_id:
                cluster_indices.append(i)

        if not cluster_indices:
            return []

        embeddings = np.array(all_data["embeddings"])
        cluster_embeddings = embeddings[cluster_indices]

        # Calculate centroid
        centroid = cluster_embeddings.mean(axis=0)

        # Calculate distances from centroid
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)

        # Get indices of farthest articles
        boundary_local_indices = np.argsort(distances)[-n:][::-1]

        articles = []
        for local_idx in boundary_local_indices:
            global_idx = cluster_indices[local_idx]
            articles.append({
                "id": all_data["ids"][global_idx],
                "distance_from_centroid": float(distances[local_idx]),
                **all_data["metadatas"][global_idx],
            })

        return articles

    def get_article(self, article_id: str) -> Optional[dict]:
        """Get a single article by ID."""
        try:
            result = self._collection.get(ids=[article_id], include=["metadatas"])
            if result["ids"]:
                return {"id": result["ids"][0], **result["metadatas"][0]}
        except Exception:
            pass
        return None

    def get_topology_info(self) -> list[ClusterInfo]:
        """Get topology overview with cluster information."""
        all_data = self._collection.get(include=["metadatas"])
        if not all_data["ids"]:
            return []

        total = len(all_data["ids"])

        # Group by cluster
        clusters: dict[int, list[dict]] = {}
        for i, meta in enumerate(all_data["metadatas"]):
            cid = meta.get("cluster_id", -1)
            if cid == -1:
                continue
            if cid not in clusters:
                clusters[cid] = []
            clusters[cid].append({"id": all_data["ids"][i], **meta})

        # Get Thompson Sampling state
        arms = {a["cluster_id"]: a for a in get_all_cluster_arms()}

        result = []
        for cid, articles in sorted(clusters.items()):
            arm = arms.get(cid, {})
            sample_titles = [a.get("original_title", "")[:80] for a in articles[:3]]

            result.append(ClusterInfo(
                cluster_id=cid,
                article_count=len(articles),
                density=len(articles) / total if total > 0 else 0,
                label=arm.get("label", ""),
                alpha=arm.get("alpha", 1.0),
                beta=arm.get("beta", 1.0),
                sample_titles=sample_titles,
            ))

        return result

    def get_total_articles(self) -> int:
        """Get total number of articles in the collection."""
        return self._collection.count()
