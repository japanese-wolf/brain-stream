"""Base LLM provider interface for CLI-based LLM integration."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    """Supported LLM CLI providers."""

    CLAUDE_CODE = "claude"
    GITHUB_COPILOT = "copilot"


@dataclass
class SummaryResult:
    """Result of article summarization."""

    title: str
    """AI-generated summary title."""

    content: str
    """AI-generated summary content."""

    diff_description: Optional[str] = None
    """Description of what changed (if applicable)."""

    explanation: Optional[str] = None
    """Technical explanation of the update's impact."""


@dataclass
class TagResult:
    """Result of tag extraction."""

    tags: list[str] = field(default_factory=list)
    """Extracted tags/categories."""

    vendor_services: list[str] = field(default_factory=list)
    """Specific vendor services mentioned (e.g., 'Lambda', 'S3')."""


@dataclass
class RelevanceResult:
    """Result of relevance analysis."""

    score: float
    """Relevance score from 0.0 to 1.0."""

    matched_tech_stack: list[str] = field(default_factory=list)
    """Tech stack items that matched."""

    reason: str = ""
    """Brief explanation of relevance."""


@dataclass
class ProcessingResult:
    """Combined result of all LLM processing."""

    summary: SummaryResult
    tags: TagResult
    relevance: Optional[RelevanceResult] = None

    # Metadata
    provider: str = ""
    model: str = ""
    processing_time_ms: int = 0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    This class defines the interface for CLI-based LLM integration.
    Implementations call external CLI tools (claude, gh copilot) via subprocess.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'claude', 'copilot')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the CLI tool is installed and accessible.

        Returns:
            True if the CLI is available, False otherwise.
        """
        ...

    @abstractmethod
    async def summarize(
        self,
        title: str,
        content: str,
        vendor: str,
    ) -> SummaryResult:
        """Generate a summary for an article.

        Args:
            title: Original article title.
            content: Original article content.
            vendor: Vendor name (e.g., 'AWS', 'GCP').

        Returns:
            SummaryResult with generated title, content, and explanations.
        """
        ...

    @abstractmethod
    async def extract_tags(
        self,
        title: str,
        content: str,
        vendor: str,
    ) -> TagResult:
        """Extract tags and categories from an article.

        Args:
            title: Article title.
            content: Article content.
            vendor: Vendor name.

        Returns:
            TagResult with extracted tags and services.
        """
        ...

    @abstractmethod
    async def analyze_relevance(
        self,
        title: str,
        content: str,
        tech_stack: list[str],
    ) -> RelevanceResult:
        """Analyze relevance of an article to user's tech stack.

        Args:
            title: Article title.
            content: Article content.
            tech_stack: User's registered tech stack.

        Returns:
            RelevanceResult with score and matched items.
        """
        ...

    async def process_article(
        self,
        title: str,
        content: str,
        vendor: str,
        tech_stack: Optional[list[str]] = None,
    ) -> ProcessingResult:
        """Process an article through the full LLM pipeline.

        This is a convenience method that runs summarize, extract_tags,
        and optionally analyze_relevance in sequence.

        Args:
            title: Original article title.
            content: Original article content.
            vendor: Vendor name.
            tech_stack: Optional user's tech stack for relevance analysis.

        Returns:
            ProcessingResult with all processing results.
        """
        import time

        start_time = time.time()

        # Run summarization
        summary = await self.summarize(title, content, vendor)

        # Extract tags
        tags = await self.extract_tags(title, content, vendor)

        # Analyze relevance if tech stack provided
        relevance = None
        if tech_stack:
            relevance = await self.analyze_relevance(title, content, tech_stack)

        processing_time = int((time.time() - start_time) * 1000)

        return ProcessingResult(
            summary=summary,
            tags=tags,
            relevance=relevance,
            provider=self.name,
            model="cli",
            processing_time_ms=processing_time,
        )


class LLMError(Exception):
    """Base exception for LLM errors."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"[{provider}] {message}")


class CLINotFoundError(LLMError):
    """CLI tool not found."""

    pass


class ProcessingError(LLMError):
    """Error during LLM processing."""

    pass


class TimeoutError(LLMError):
    """LLM processing timed out."""

    pass
