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

    related_technologies: list[str] = field(default_factory=list)
    """Technologies related to this article that the user should know about."""

    tech_stack_connection: Optional[str] = None
    """How this article connects to the user's tech stack."""


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
    async def analyze(
        self,
        title: str,
        content: str,
        vendor: str,
        tech_stack: Optional[list[str]] = None,
        domains: Optional[list[str]] = None,
        roles: Optional[list[str]] = None,
        goals: Optional[list[str]] = None,
    ) -> ProcessingResult:
        """Analyze an article in a single LLM call.

        Extracts summary, tags, and discovery fields in one unified prompt
        to minimize token consumption.

        Args:
            title: Original article title.
            content: Original article content.
            vendor: Vendor name (e.g., 'AWS', 'GCP').
            tech_stack: Optional user's tech stack for personalized analysis.
            domains: Optional user's domains (e.g., ['serverless', 'mlops']).
            roles: Optional user's roles (e.g., ['backend', 'infra']).
            goals: Optional user's goals (e.g., ['tech-selection']).

        Returns:
            ProcessingResult with all processing results.
        """
        ...

    async def process_article(
        self,
        title: str,
        content: str,
        vendor: str,
        tech_stack: Optional[list[str]] = None,
        domains: Optional[list[str]] = None,
        roles: Optional[list[str]] = None,
        goals: Optional[list[str]] = None,
    ) -> ProcessingResult:
        """Process an article through the LLM pipeline.

        Delegates to analyze() which performs all extraction in a single call.

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

        result = await self.analyze(
            title, content, vendor, tech_stack, domains, roles, goals
        )

        result.processing_time_ms = int((time.time() - start_time) * 1000)
        result.provider = self.name
        result.model = "cli"

        return result


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
