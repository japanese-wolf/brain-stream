"""Claude Code CLI provider for v2 LLM processing."""

import asyncio
import json
import re
import shutil
from typing import Optional

from brainstream.llm.base import (
    BaseLLMProvider,
    CLINotFoundError,
    ProcessingError,
    ProcessingResult,
    TimeoutError,
)


class ClaudeCodeProvider(BaseLLMProvider):
    """LLM provider using Claude Code CLI.

    v2: Simplified prompt focused on summarization, tagging,
    primary source detection, and tech domain classification.
    """

    def __init__(self, timeout: int = 120):
        self._timeout = timeout
        self._claude_path: Optional[str] = None

    @property
    def name(self) -> str:
        return "claude"

    @property
    def display_name(self) -> str:
        return "Claude Code"

    async def is_available(self) -> bool:
        self._claude_path = shutil.which("claude")
        return self._claude_path is not None

    async def _run_claude(self, prompt: str) -> str:
        if not await self.is_available():
            raise CLINotFoundError(
                self.name,
                "Claude Code CLI not found. Install from: https://claude.ai/code",
            )

        try:
            process = await asyncio.create_subprocess_exec(
                self._claude_path,
                "-p",
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
        url: str,
        vendor: str,
    ) -> ProcessingResult:
        """Analyze an article with v2 prompt."""
        prompt = f"""You are a technical intelligence analyst. Analyze this technology article and extract structured metadata.

Title: {title}
URL: {url}
Vendor: {vendor}

Content:
{content[:3000]}

Respond in this exact JSON format:
{{
    "summary": "2-3 sentence summary of what this announcement means for engineers",
    "tags": ["category tags like compute, database, security, ai, devops, frontend, networking"],
    "is_primary_source": true or false (true if this URL is an official vendor announcement/blog/changelog, false if it's a third-party blog/news article about the vendor),
    "tech_domain": "primary technology domain (e.g., serverless, container-orchestration, machine-learning, database, security, networking, observability, ci-cd, frontend, iac)"
}}

Rules:
- is_primary_source should be true for URLs from official vendor domains (e.g., aws.amazon.com, cloud.google.com, openai.com, github.blog, docs.anthropic.com)
- tech_domain should be a single hyphenated keyword describing the main technology area
- tags should be 2-5 general category labels
- summary should be concise and actionable for engineers

Respond with ONLY the JSON, no other text."""

        response = await self._run_claude(prompt)

        try:
            data = self._extract_json(response)

            return ProcessingResult(
                summary=data.get("summary", content[:200]),
                tags=data.get("tags", []),
                is_primary_source=data.get("is_primary_source", False),
                tech_domain=data.get("tech_domain", ""),
            )

        except Exception:
            return ProcessingResult(
                summary=content[:200] if content else title,
                tags=[vendor.lower()],
                is_primary_source=False,
                tech_domain="",
            )

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text."""
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

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
