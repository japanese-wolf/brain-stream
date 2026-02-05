"""LLM provider registry."""

from typing import Optional

from brainstream.llm.base import BaseLLMProvider, LLMProvider


class LLMRegistry:
    """Registry for LLM providers.

    Manages available LLM providers and provides a way to get
    the appropriate provider based on configuration.
    """

    _instance: Optional["LLMRegistry"] = None
    _providers: dict[str, type[BaseLLMProvider]]

    def __new__(cls) -> "LLMRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._load_providers()
        return cls._instance

    def _load_providers(self) -> None:
        """Load built-in providers."""
        from brainstream.llm.claude_code import ClaudeCodeProvider

        self._providers = {
            LLMProvider.CLAUDE_CODE.value: ClaudeCodeProvider,
        }

    def get(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """Get a provider instance by name.

        Args:
            provider_name: Provider name (e.g., 'claude', 'copilot').

        Returns:
            Provider instance or None if not found.
        """
        provider_cls = self._providers.get(provider_name)
        if provider_cls:
            return provider_cls()
        return None

    def list_providers(self) -> list[str]:
        """List available provider names."""
        return list(self._providers.keys())

    async def get_available(self) -> Optional[BaseLLMProvider]:
        """Get the first available provider.

        Checks each registered provider and returns the first one
        that is available (CLI installed).

        Returns:
            First available provider or None.
        """
        for name in self._providers:
            provider = self.get(name)
            if provider and await provider.is_available():
                return provider
        return None


# Global registry instance
llm_registry = LLMRegistry()
