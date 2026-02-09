"""LLM provider registry."""

from typing import Optional

from brainstream.llm.base import BaseLLMProvider, LLMProvider


class LLMRegistry:
    """Registry for LLM providers."""

    _instance: Optional["LLMRegistry"] = None
    _providers: dict[str, type[BaseLLMProvider]]

    def __new__(cls) -> "LLMRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._load_providers()
        return cls._instance

    def _load_providers(self) -> None:
        from brainstream.llm.claude_code import ClaudeCodeProvider

        self._providers = {
            LLMProvider.CLAUDE_CODE.value: ClaudeCodeProvider,
        }

    def get(self, provider_name: str) -> Optional[BaseLLMProvider]:
        provider_cls = self._providers.get(provider_name)
        if provider_cls:
            return provider_cls()
        return None

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    async def get_available(self) -> Optional[BaseLLMProvider]:
        for name in self._providers:
            provider = self.get(name)
            if provider and await provider.is_available():
                return provider
        return None


llm_registry = LLMRegistry()
