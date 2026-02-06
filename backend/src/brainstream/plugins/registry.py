"""Plugin registry for discovering and managing data source plugins."""

from importlib.metadata import entry_points
from typing import Optional

from brainstream.plugins.base import BaseSourcePlugin, PluginInfo


class PluginRegistry:
    """Registry for managing data source plugins.

    Plugins can be registered:
    1. Built-in: Automatically loaded from brainstream.plugins.builtin
    2. Entry points: Discovered via 'brainstream.plugins' entry point group
    3. Manual: Registered programmatically via register()
    """

    _instance: Optional["PluginRegistry"] = None
    _plugins: dict[str, type[BaseSourcePlugin]]
    _initialized: bool

    def __new__(cls) -> "PluginRegistry":
        """Singleton pattern for plugin registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins = {}
            cls._instance._initialized = False
        return cls._instance

    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins from brainstream.plugins.builtin."""
        from brainstream.plugins.builtin import (
            AnthropicChangelogPlugin,
            AWSWhatsNewPlugin,
            GCPReleaseNotesPlugin,
            GitHubPlatformPlugin,
            GitHubReleasesPlugin,
            OpenAIChangelogPlugin,
        )

        # Register built-in plugins
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
        """Discover plugins via entry points."""
        try:
            eps = entry_points(group="brainstream.plugins")
            for ep in eps:
                try:
                    plugin_cls = ep.load()
                    if issubclass(plugin_cls, BaseSourcePlugin):
                        self.register(plugin_cls)
                except Exception as e:
                    # Log but don't fail on plugin load errors
                    print(f"Warning: Failed to load plugin {ep.name}: {e}")
        except Exception:
            # entry_points might not be available in all Python versions
            pass

    def initialize(self) -> None:
        """Initialize the registry by loading all plugins."""
        if self._initialized:
            return

        self._load_builtin_plugins()
        self._discover_entry_points()
        self._initialized = True

    def register(self, plugin_cls: type[BaseSourcePlugin]) -> None:
        """Register a plugin class.

        Args:
            plugin_cls: Plugin class (not instance) to register.
        """
        # Create a temporary instance to get plugin info
        try:
            instance = plugin_cls()
            info = instance.info
            self._plugins[info.name] = plugin_cls
        except Exception as e:
            print(f"Warning: Failed to register plugin {plugin_cls}: {e}")

    def unregister(self, name: str) -> bool:
        """Unregister a plugin by name.

        Args:
            name: Plugin name to unregister.

        Returns:
            True if plugin was unregistered, False if not found.
        """
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False

    def get(self, name: str) -> Optional[BaseSourcePlugin]:
        """Get a plugin instance by name.

        Args:
            name: Plugin name.

        Returns:
            Plugin instance or None if not found.
        """
        self.initialize()
        plugin_cls = self._plugins.get(name)
        if plugin_cls:
            return plugin_cls()
        return None

    def list_plugins(self) -> list[PluginInfo]:
        """List all registered plugins.

        Returns:
            List of PluginInfo for all registered plugins.
        """
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
        """Get instances of all registered plugins.

        Returns:
            List of plugin instances.
        """
        self.initialize()
        result = []
        for plugin_cls in self._plugins.values():
            try:
                result.append(plugin_cls())
            except Exception:
                pass
        return result

    def get_by_vendor(self, vendor: str) -> list[BaseSourcePlugin]:
        """Get all plugins for a specific vendor.

        Args:
            vendor: Vendor name (e.g., 'AWS', 'GCP').

        Returns:
            List of plugin instances for the vendor.
        """
        return [p for p in self.get_all() if p.info.vendor.lower() == vendor.lower()]


# Global registry instance
registry = PluginRegistry()
