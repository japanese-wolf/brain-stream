"""Article database model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from brainstream.core.database import Base


class Article(Base):
    """Article model representing a news item from a data source."""

    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Source reference
    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("data_sources.id"),
        nullable=True,
    )

    # External identifier for deduplication
    external_id: Mapped[str] = mapped_column(String(255), index=True)

    # Primary source link (required)
    primary_source_url: Mapped[str] = mapped_column(Text, nullable=False)

    # Original content from source
    original_title: Mapped[str] = mapped_column(Text, nullable=False)
    original_content: Mapped[str] = mapped_column(Text, nullable=False)

    # AI-generated content (nullable until processed)
    summary_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diff_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Discovery fields (Phase 1: Direction B)
    related_technologies: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tech_stack_connection: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Categorization
    vendor: Mapped[str] = mapped_column(String(100), index=True)
    tags: Mapped[dict] = mapped_column(JSON, default=list)

    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # LLM info
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    source: Mapped[Optional["DataSource"]] = relationship(
        "DataSource",
        back_populates="articles",
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title={self.original_title[:50]}...)>"

    @property
    def is_processed(self) -> bool:
        """Check if article has been processed by LLM."""
        return self.processed_at is not None

    @property
    def display_title(self) -> str:
        """Get the best title to display (summary if available, else original)."""
        return self.summary_title or self.original_title


class DataSource(Base):
    """Data source configuration model."""

    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Plugin reference
    plugin_name: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    vendor: Mapped[str] = mapped_column(String(100), index=True)

    # Status
    enabled: Mapped[bool] = mapped_column(default=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Fetch tracking
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fetch_status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    articles: Mapped[list["Article"]] = relationship(
        "Article",
        back_populates="source",
    )

    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, name={self.name})>"


class UserProfile(Base):
    """User profile for personalization."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Tech stack preferences
    tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    preferred_vendors: Mapped[list] = mapped_column(JSON, default=list)

    # Extended profile (Phase 3)
    domains: Mapped[list] = mapped_column(JSON, default=list)
    roles: Mapped[list] = mapped_column(JSON, default=list)
    goals: Mapped[list] = mapped_column(JSON, default=list)

    # LLM settings
    llm_provider: Mapped[str] = mapped_column(String(50), default="claude")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id})>"
