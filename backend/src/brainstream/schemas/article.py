"""Pydantic schemas for articles."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ArticleBase(BaseModel):
    """Base article schema."""

    original_title: str
    primary_source_url: str
    vendor: str


class ArticleCreate(ArticleBase):
    """Schema for creating an article."""

    external_id: str
    original_content: str
    published_at: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)


class ArticleResponse(ArticleBase):
    """Schema for article response."""

    id: str
    source_id: Optional[str] = None

    # Original content
    original_content: str

    # AI-generated content
    summary_title: Optional[str] = None
    summary_content: Optional[str] = None
    diff_description: Optional[str] = None
    explanation: Optional[str] = None

    # Discovery fields (Phase 1: Direction B)
    related_technologies: list[str] = Field(default_factory=list)
    tech_stack_connection: Optional[str] = None

    # Metadata
    tags: list[str] = Field(default_factory=list)
    published_at: Optional[datetime] = None
    collected_at: datetime
    processed_at: Optional[datetime] = None

    # LLM info
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None

    class Config:
        from_attributes = True

    @property
    def is_processed(self) -> bool:
        """Check if article has been processed."""
        return self.processed_at is not None

    @property
    def display_title(self) -> str:
        """Get the best title to display."""
        return self.summary_title or self.original_title


class ArticleListResponse(BaseModel):
    """Schema for paginated article list response."""

    items: list[ArticleResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ArticleListParams(BaseModel):
    """Query parameters for listing articles."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    vendor: Optional[str] = None
    tags: Optional[list[str]] = None
    processed_only: bool = False
    tech_stack_filter: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class RelevanceScoreResponse(BaseModel):
    """Relevance score for an article."""

    total_score: float = Field(..., description="Overall relevance score (0.0 to 1.0)")
    tag_score: float = Field(..., description="Score from tag matching")
    vendor_score: float = Field(..., description="Score from vendor matching")
    content_score: float = Field(..., description="Score from content keyword matching")
    relevance_level: str = Field(..., description="Human-readable level: high, medium, low, none")
    matched_tags: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)


class ArticleWithRelevanceResponse(ArticleResponse):
    """Article response with relevance scoring."""

    relevance: Optional[RelevanceScoreResponse] = None


class TrendingTechnologyResponse(BaseModel):
    """A technology trending in the user's field (Phase 2: Direction A)."""

    name: str = Field(..., description="Technology name")
    count: int = Field(..., description="Number of articles where this co-occurs with tech stack")
    related_to: list[str] = Field(default_factory=list, description="Which tech stack tags it co-occurs with")
    sample_article_ids: list[str] = Field(default_factory=list, description="Sample article IDs (max 3)")


class FeedResponse(BaseModel):
    """Response for the personalized feed endpoint."""

    items: list[ArticleWithRelevanceResponse]
    trending_technologies: list[TrendingTechnologyResponse] = Field(
        default_factory=list, description="Technologies trending near user's tech stack"
    )
    total: int
    page: int
    per_page: int
    pages: int
    tech_stack: list[str] = Field(default_factory=list, description="User's tech stack used for scoring")
    preferred_vendors: list[str] = Field(default_factory=list)
