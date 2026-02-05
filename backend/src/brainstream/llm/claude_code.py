"""Claude Code CLI provider for LLM processing."""

import asyncio
import json
import shutil
from typing import Optional

from brainstream.llm.base import (
    BaseLLMProvider,
    CLINotFoundError,
    ProcessingError,
    RelevanceResult,
    SummaryResult,
    TagResult,
    TimeoutError,
)


class ClaudeCodeProvider(BaseLLMProvider):
    """LLM provider using Claude Code CLI.

    This provider uses the `claude` command-line tool to process articles.
    It leverages the user's existing Claude Max/Pro/API subscription.

    Requirements:
        - Claude Code CLI installed (`claude` command available)
        - Valid Claude subscription (Max, Pro, or API)
    """

    def __init__(self, timeout: int = 120):
        """Initialize the provider.

        Args:
            timeout: Maximum time in seconds for CLI operations.
        """
        self._timeout = timeout
        self._claude_path: Optional[str] = None

    @property
    def name(self) -> str:
        return "claude"

    @property
    def display_name(self) -> str:
        return "Claude Code"

    async def is_available(self) -> bool:
        """Check if claude CLI is installed."""
        self._claude_path = shutil.which("claude")
        return self._claude_path is not None

    async def _run_claude(self, prompt: str) -> str:
        """Run claude CLI with a prompt.

        Args:
            prompt: The prompt to send to Claude.

        Returns:
            Claude's response text.

        Raises:
            CLINotFoundError: If claude CLI is not found.
            TimeoutError: If the operation times out.
            ProcessingError: If claude returns an error.
        """
        if not await self.is_available():
            raise CLINotFoundError(
                self.name,
                "Claude Code CLI not found. Install from: https://claude.ai/code",
            )

        try:
            process = await asyncio.create_subprocess_exec(
                self._claude_path,
                "-p",  # Print mode (non-interactive)
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self._timeout,
            )

            if process.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                raise ProcessingError(self.name, f"CLI error: {error_msg}")

            return stdout.decode().strip()

        except asyncio.TimeoutError:
            raise TimeoutError(
                self.name,
                f"Processing timed out after {self._timeout} seconds",
            )
        except Exception as e:
            if isinstance(e, (CLINotFoundError, TimeoutError, ProcessingError)):
                raise
            raise ProcessingError(self.name, f"Unexpected error: {e}")

    async def summarize(
        self,
        title: str,
        content: str,
        vendor: str,
    ) -> SummaryResult:
        """Generate a summary using Claude Code CLI."""
        prompt = f"""You are a technical writer summarizing cloud/AI vendor announcements for engineers.

Analyze this {vendor} announcement and provide:
1. A concise summary title (max 100 chars)
2. A brief summary (2-3 sentences)
3. What specifically changed or was added
4. Technical impact for developers

Original Title: {title}

Content:
{content[:3000]}

Respond in this exact JSON format:
{{
    "title": "concise summary title",
    "content": "2-3 sentence summary",
    "diff_description": "what changed",
    "explanation": "technical impact"
}}

Respond with ONLY the JSON, no other text."""

        response = await self._run_claude(prompt)

        try:
            # Try to parse JSON from response
            data = self._extract_json(response)
            return SummaryResult(
                title=data.get("title", title),
                content=data.get("content", content[:200]),
                diff_description=data.get("diff_description"),
                explanation=data.get("explanation"),
            )
        except Exception:
            # Fallback: use response as content
            return SummaryResult(
                title=title,
                content=response[:500] if response else content[:200],
            )

    async def extract_tags(
        self,
        title: str,
        content: str,
        vendor: str,
    ) -> TagResult:
        """Extract tags using Claude Code CLI."""
        prompt = f"""Analyze this {vendor} announcement and extract:
1. General tags/categories (e.g., "compute", "database", "security", "ai")
2. Specific {vendor} services mentioned (e.g., "Lambda", "S3", "EC2")

Title: {title}

Content:
{content[:2000]}

Respond in this exact JSON format:
{{
    "tags": ["tag1", "tag2"],
    "vendor_services": ["Service1", "Service2"]
}}

Respond with ONLY the JSON, no other text."""

        response = await self._run_claude(prompt)

        try:
            data = self._extract_json(response)
            return TagResult(
                tags=data.get("tags", []),
                vendor_services=data.get("vendor_services", []),
            )
        except Exception:
            return TagResult(tags=[vendor.lower()])

    async def analyze_relevance(
        self,
        title: str,
        content: str,
        tech_stack: list[str],
    ) -> RelevanceResult:
        """Analyze relevance to user's tech stack using Claude Code CLI."""
        tech_stack_str = ", ".join(tech_stack)

        prompt = f"""Analyze how relevant this announcement is to a developer using: {tech_stack_str}

Title: {title}

Content:
{content[:2000]}

Respond in this exact JSON format:
{{
    "score": 0.0 to 1.0,
    "matched_tech_stack": ["matching", "items"],
    "reason": "brief explanation"
}}

Score guidelines:
- 1.0: Directly about a technology in the stack
- 0.7-0.9: Related feature or integration
- 0.4-0.6: Same vendor, different service
- 0.1-0.3: Tangentially related
- 0.0: Not relevant

Respond with ONLY the JSON, no other text."""

        response = await self._run_claude(prompt)

        try:
            data = self._extract_json(response)
            return RelevanceResult(
                score=float(data.get("score", 0.5)),
                matched_tech_stack=data.get("matched_tech_stack", []),
                reason=data.get("reason", ""),
            )
        except Exception:
            return RelevanceResult(score=0.5, reason="Unable to analyze")

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text.

        Handles cases where the response includes markdown code blocks.
        """
        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract from code blocks
        import re

        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"\{.*\}",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if "```" in pattern else match.group(0)
                    return json.loads(json_str)
                except (json.JSONDecodeError, IndexError):
                    continue

        raise ValueError(f"Could not extract JSON from response: {text[:200]}")
