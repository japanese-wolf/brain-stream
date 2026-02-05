"""Article API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from brainstream.core.database import get_db
from brainstream.models.article import Article, UserProfile
from brainstream.schemas.article import (
    ArticleListResponse,
    ArticleResponse,
    ArticleWithRelevanceResponse,
    FeedResponse,
    RelevanceScoreResponse,
)
from brainstream.services.relevance import RelevanceService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    vendor: Optional[str] = None,
    processed_only: bool = False,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> ArticleListResponse:
    """List articles with pagination and filtering.

    Args:
        page: Page number (1-indexed)
        per_page: Number of items per page
        vendor: Filter by vendor (e.g., 'AWS', 'GCP')
        processed_only: Only return processed articles
        date_from: Filter articles published after this date
        date_to: Filter articles published before this date

    Returns:
        Paginated list of articles
    """
    # Build query
    query = select(Article)

    # Apply filters
    if vendor:
        query = query.where(Article.vendor == vendor)

    if processed_only:
        query = query.where(Article.processed_at.isnot(None))

    if date_from:
        query = query.where(Article.published_at >= date_from)

    if date_to:
        query = query.where(Article.published_at <= date_to)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(Article.published_at.desc().nullsfirst())
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute query
    result = await db.execute(query)
    articles = result.scalars().all()

    # Calculate pages
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in articles],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


# IMPORTANT: Specific routes must come BEFORE the catch-all /{article_id} route


@router.get("/feed", response_model=FeedResponse)
async def get_personalized_feed(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    min_relevance: float = Query(default=0.0, ge=0.0, le=1.0),
    sort_by: str = Query(default="relevance", pattern="^(relevance|date)$"),
    vendor: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> FeedResponse:
    """Get personalized feed based on user's tech stack.

    Articles are scored for relevance based on the user's registered
    tech stack and preferred vendors. High-relevance articles appear first.

    Args:
        page: Page number (1-indexed)
        per_page: Number of items per page
        min_relevance: Minimum relevance score to include (0.0 to 1.0)
        sort_by: Sort order - "relevance" (default) or "date"
        vendor: Optional vendor filter

    Returns:
        Personalized feed with relevance scores
    """
    # Get user profile
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    tech_stack = profile.tech_stack if profile else []
    preferred_vendors = profile.preferred_vendors if profile else []

    # Build query
    query = select(Article)

    if vendor:
        query = query.where(Article.vendor == vendor)

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_db = total_result.scalar() or 0

    # Fetch all articles (we need to score them all for proper sorting)
    # In production, this should be optimized with caching or pre-computed scores
    query = query.order_by(Article.published_at.desc().nullsfirst())
    result = await db.execute(query)
    all_articles = result.scalars().all()

    # Initialize relevance service
    relevance_service = RelevanceService(
        tech_stack=tech_stack,
        preferred_vendors=preferred_vendors,
    )

    # Score and filter articles
    if sort_by == "relevance":
        scored_articles = relevance_service.prioritize_feed(
            all_articles, high_relevance_first=True
        )
    else:
        scored_articles = relevance_service.prioritize_feed(
            all_articles, high_relevance_first=False
        )

    # Filter by minimum relevance
    if min_relevance > 0:
        scored_articles = [
            (a, s) for a, s in scored_articles if s.total_score >= min_relevance
        ]

    total = len(scored_articles)
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    # Paginate
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_articles = scored_articles[start_idx:end_idx]

    # Build response
    items = []
    for article, score in page_articles:
        article_response = ArticleWithRelevanceResponse.model_validate(article)
        article_response.relevance = RelevanceScoreResponse(
            total_score=score.total_score,
            tag_score=score.tag_score,
            vendor_score=score.vendor_score,
            content_score=score.content_score,
            relevance_level=score.relevance_level,
            matched_tags=score.matched_tags,
            matched_keywords=score.matched_keywords,
        )
        items.append(article_response)

    return FeedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        tech_stack=tech_stack,
        preferred_vendors=preferred_vendors,
    )


@router.get("/vendor/{vendor}", response_model=ArticleListResponse)
async def list_articles_by_vendor(
    vendor: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ArticleListResponse:
    """List articles for a specific vendor.

    Args:
        vendor: Vendor name (e.g., 'AWS', 'GCP')
        page: Page number
        per_page: Items per page

    Returns:
        Paginated list of articles
    """
    return await list_articles(
        page=page,
        per_page=per_page,
        vendor=vendor,
        db=db,
    )


# Catch-all routes with path parameters must come LAST


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> ArticleResponse:
    """Get a single article by ID.

    Args:
        article_id: Article UUID

    Returns:
        Article details

    Raises:
        HTTPException: If article not found
    """
    query = select(Article).where(Article.id == article_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleResponse.model_validate(article)


@router.get("/{article_id}/relevance", response_model=RelevanceScoreResponse)
async def get_article_relevance(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> RelevanceScoreResponse:
    """Get relevance score for a specific article.

    Args:
        article_id: Article UUID

    Returns:
        Relevance score breakdown

    Raises:
        HTTPException: If article not found
    """
    # Get article
    query = select(Article).where(Article.id == article_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Get user profile
    profile_result = await db.execute(select(UserProfile).limit(1))
    profile = profile_result.scalar_one_or_none()

    tech_stack = profile.tech_stack if profile else []
    preferred_vendors = profile.preferred_vendors if profile else []

    # Calculate relevance
    relevance_service = RelevanceService(
        tech_stack=tech_stack,
        preferred_vendors=preferred_vendors,
    )
    score = relevance_service.calculate_score(article)

    return RelevanceScoreResponse(
        total_score=score.total_score,
        tag_score=score.tag_score,
        vendor_score=score.vendor_score,
        content_score=score.content_score,
        relevance_level=score.relevance_level,
        matched_tags=score.matched_tags,
        matched_keywords=score.matched_keywords,
    )
