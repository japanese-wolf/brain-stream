"""Base LLM provider interface for v2."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    """Supported LLM CLI providers."""

    CLAUDE_CODE = "claude"
    GITHUB_COPILOT = "copilot"


@dataclass
class ProcessingResult:
    """Result of LLM article processing for v2.

    Simplified from v1: no relevance scoring, no personalization fields.
    Added: is_primary_source, tech_domain for topology mapping.
    """

    summary: str
    """AI-generated summary (2-3 sentences)."""

    tags: list[str] = field(default_factory=list)
    """Extracted tags/categories."""

    is_primary_source: bool = False
    """Whether this is a primary source (vendor official announcement)."""

    tech_domain: str = ""
    """Primary technology domain (e.g., 'container-orchestration', 'serverless')."""

    # Metadata
    provider: str = ""
    model: str = ""
    processing_time_ms: int = 0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        ...

    @abstractmethod
    async def analyze(
        self,
        title: str,
        content: str,
        url: str,
        vendor: str,
    ) -> ProcessingResult:
        """Analyze an article: summarize, tag, detect primary source, classify domain."""
        ...

    async def process_article(
        self,
        title: str,
        content: str,
        url: str,
        vendor: str,
    ) -> ProcessingResult:
        """Process an article through the LLM pipeline."""
        import time

        start_time = time.time()
        result = await self.analyze(title, content, url, vendor)
        result.processing_time_ms = int((time.time() - start_time) * 1000)
        result.provider = self.name
        result.model = "cli"
        return result


class LLMError(Exception):
    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"[{provider}] {message}")


class CLINotFoundError(LLMError):
    pass


class ProcessingError(LLMError):
    pass


class TimeoutError(LLMError):
    pass
