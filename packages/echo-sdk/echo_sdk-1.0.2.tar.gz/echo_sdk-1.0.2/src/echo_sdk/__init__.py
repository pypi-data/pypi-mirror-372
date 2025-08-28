"""Echo Plugin SDK - Bridge library for Echo multi-agent system plugins.

This SDK provides the interface between Echo core system and plugins,
enabling true decoupling and independent plugin bin.

Example usage:
    >>> from echo_sdk import BasePlugin, PluginMetadata, tool
    >>>
    >>> class MyPlugin(BasePlugin):
    ...     @staticmethod
    ...     def get_metadata() -> PluginMetadata:
    ...         return PluginMetadata(name="my_plugin", version="1.0.1")
    ...
    ...     @staticmethod
    ...     def create_agent():
    ...         return MyAgent()
"""

from importlib.metadata import version

from .base.agent import BasePluginAgent
from .base.metadata import ModelConfig, PluginMetadata
from .base.plugin import BasePlugin
from .registry.contracts import PluginContract
from .registry.plugin_registry import (
    discover_plugins,
    get_plugin_registry,
    register_plugin,
)
from .tools.decorators import tool
from .types.state import AgentState
from .utils.directory_discovery import (
    get_directory_discovery_summary,
    import_plugins_from_directories,
    list_imported_directory_modules,
    list_loaded_directories,
    reset_directory_discovery,
)
from .utils.environment_discovery import (
    get_environment_discovery_summary,
    import_plugins_from_environment,
    list_imported_environment_packages,
    list_installed_environment_packages,
    reset_environment_discovery,
)

try:
    __version__ = version("echo_sdk")
except Exception:
    __version__ = "unknown"

__all__ = [
    # Core interfaces
    "BasePlugin",
    "BasePluginAgent",
    "PluginMetadata",
    "ModelConfig",
    # Tools
    "tool",
    # Registry
    "PluginContract",
    "register_plugin",
    "discover_plugins",
    "get_plugin_registry",
    # Plugin Discovery
    "import_plugins_from_environment",
    "import_plugins_from_directories",
    "get_environment_discovery_summary",
    "list_installed_environment_packages",
    "list_imported_environment_packages",
    "reset_environment_discovery",
    # Directory Discovery helpers
    "reset_directory_discovery",
    "get_directory_discovery_summary",
    "list_loaded_directories",
    # Types
    "AgentState",
]
