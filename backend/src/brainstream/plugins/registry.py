"""Plugin registry for discovering and managing data source plugins."""

from importlib.metadata import entry_points
from typing import Optional

from brainstream.plugins.base import BaseSourcePlugin, PluginInfo


class PluginRegistry:
    """Registry for managing data source plugins."""

    _instance: Optional["PluginRegistry"] = None
    _plugins: dict[str, type[BaseSourcePlugin]]
    _initialized: bool

    def __new__(cls) -> "PluginRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins = {}
            cls._instance._initialized = False
        return cls._instance

    def _load_builtin_plugins(self) -> None:
        from brainstream.plugins.builtin import (
            AnthropicChangelogPlugin,
            AWSWhatsNewPlugin,
            GCPReleaseNotesPlugin,
            GitHubPlatformPlugin,
            GitHubReleasesPlugin,
            OpenAIChangelogPlugin,
        )

        builtin_plugins = [
            AWSWhatsNewPlugin,
            GCPReleaseNotesPlugin,
            OpenAIChangelogPlugin,
            AnthropicChangelogPlugin,
            GitHubPlatformPlugin,
            GitHubReleasesPlugin,
        ]

        for plugin_cls in builtin_plugins:
            self.register(plugin_cls)

    def _discover_entry_points(self) -> None:
        try:
            eps = entry_points(group="brainstream.plugins")
            for ep in eps:
                try:
                    plugin_cls = ep.load()
                    if issubclass(plugin_cls, BaseSourcePlugin):
                        self.register(plugin_cls)
                except Exception as e:
                    print(f"Warning: Failed to load plugin {ep.name}: {e}")
        except Exception:
            pass

    def initialize(self) -> None:
        if self._initialized:
            return
        self._load_builtin_plugins()
        self._discover_entry_points()
        self._initialized = True

    def register(self, plugin_cls: type[BaseSourcePlugin]) -> None:
        try:
            instance = plugin_cls()
            info = instance.info
            self._plugins[info.name] = plugin_cls
        except Exception as e:
            print(f"Warning: Failed to register plugin {plugin_cls}: {e}")

    def unregister(self, name: str) -> bool:
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False

    def get(self, name: str) -> Optional[BaseSourcePlugin]:
        self.initialize()
        plugin_cls = self._plugins.get(name)
        if plugin_cls:
            return plugin_cls()
        return None

    def list_plugins(self) -> list[PluginInfo]:
        self.initialize()
        result = []
        for plugin_cls in self._plugins.values():
            try:
                instance = plugin_cls()
                result.append(instance.info)
            except Exception:
                pass
        return result

    def get_all(self) -> list[BaseSourcePlugin]:
        self.initialize()
        result = []
        for plugin_cls in self._plugins.values():
            try:
                result.append(plugin_cls())
            except Exception:
                pass
        return result

    def get_by_vendor(self, vendor: str) -> list[BaseSourcePlugin]:
        return [p for p in self.get_all() if p.info.vendor.lower() == vendor.lower()]


registry = PluginRegistry()
