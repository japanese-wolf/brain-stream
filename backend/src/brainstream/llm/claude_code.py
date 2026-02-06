"""Claude Code CLI provider for LLM processing."""

import asyncio
import json
import shutil
from typing import Optional

from brainstream.llm.base import (
    BaseLLMProvider,
    CLINotFoundError,
    ProcessingError,
    ProcessingResult,
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
        """Analyze an article in a single unified LLM call."""
        tech_stack_str = ", ".join(tech_stack) if tech_stack else ""
        has_profile = bool(tech_stack_str or domains or roles or goals)

        # Build personalization section
        personalization = ""
        if has_profile:
            profile_lines = []
            if tech_stack_str:
                profile_lines.append(f"Tech stack: {tech_stack_str}")
            if domains:
                profile_lines.append(f"Domains: {', '.join(domains)}")
            if roles:
                profile_lines.append(f"Roles: {', '.join(roles)}")
            if goals:
                profile_lines.append(f"Goals: {', '.join(goals)}")

            profile_context = "\n".join(profile_lines)
            personalization = f"""
Engineer profile:
{profile_context}

In addition to the standard analysis, provide:
- "related_technologies": Technologies related to this announcement that the engineer should explore, even if outside their current stack. Focus on technologies that are gaining relevance in this context.
- "tech_stack_connection": A concrete explanation of how this announcement connects to the engineer's profile. Be specific about implications for their domains, roles, and goals."""

        prompt = f"""You are a technical intelligence analyst helping engineers discover technology trends and understand vendor announcements.

Analyze this {vendor} announcement and provide a comprehensive analysis.

Title: {title}

Content:
{content[:3000]}
{personalization}

Respond in this exact JSON format:
{{
    "title": "concise summary title (max 100 chars)",
    "content": "2-3 sentence summary",
    "diff_description": "what specifically changed or was added",
    "explanation": "technical impact for developers",
    "tags": ["general category tags like compute, database, security, ai"],
    "vendor_services": ["specific {vendor} services mentioned"]{', "related_technologies": ["tech1", "tech2"], "tech_stack_connection": "how this connects to the engineers profile"' if has_profile else ''}
}}

Respond with ONLY the JSON, no other text."""

        response = await self._run_claude(prompt)

        try:
            data = self._extract_json(response)

            summary = SummaryResult(
                title=data.get("title", title),
                content=data.get("content", content[:200]),
                diff_description=data.get("diff_description"),
                explanation=data.get("explanation"),
                related_technologies=data.get("related_technologies", []),
                tech_stack_connection=data.get("tech_stack_connection"),
            )

            tags = TagResult(
                tags=data.get("tags", []),
                vendor_services=data.get("vendor_services", []),
            )

            return ProcessingResult(summary=summary, tags=tags)

        except Exception:
            # Fallback: minimal result
            summary = SummaryResult(
                title=title,
                content=response[:500] if response else content[:200],
            )
            tags = TagResult(tags=[vendor.lower()])
            return ProcessingResult(summary=summary, tags=tags)

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text.

        Handles cases where the response includes markdown code blocks,
        leading/trailing text, or other non-JSON content.
        """
        import re

        # Strip whitespace
        text = text.strip()

        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract from code blocks
        code_block_patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
        ]

        for pattern in code_block_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except (json.JSONDecodeError, IndexError):
                    continue

        # Try to find a JSON object by matching balanced braces
        brace_depth = 0
        start_idx = None
        for i, ch in enumerate(text):
            if ch == "{":
                if brace_depth == 0:
                    start_idx = i
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                if brace_depth == 0 and start_idx is not None:
                    try:
                        return json.loads(text[start_idx : i + 1])
                    except json.JSONDecodeError:
                        start_idx = None
                        continue

        raise ValueError(f"Could not extract JSON from response: {text[:200]}")
