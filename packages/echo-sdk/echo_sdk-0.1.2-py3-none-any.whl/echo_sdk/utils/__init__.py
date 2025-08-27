"""Utility functions for Echo plugins."""

from .directory_discovery import (
    get_directory_discovery_summary,
    import_plugins_from_directories,
    list_imported_directory_modules,
    list_loaded_directories,
    reset_directory_discovery,
)
from .environment_discovery import (
    get_environment_discovery_summary,
    import_plugins_from_environment,
    list_imported_environment_packages,
    list_installed_environment_packages,
    reset_environment_discovery,
)
from .helpers import check_compatibility, format_plugin_info, get_sdk_version
from .installers import install_packages
from .validation import validate_plugin_structure, validate_tools

__all__ = [
    # Validation
    "validate_plugin_structure",
    "validate_tools",
    # Helpers
    "get_sdk_version",
    "check_compatibility",
    "format_plugin_info",
    # Plugin Discovery
    "import_plugins_from_environment",
    "import_plugins_from_directories",
    "reset_directory_discovery",
    "get_directory_discovery_summary",
    "list_loaded_directories",
    "list_imported_directory_modules",
    "get_environment_discovery_summary",
    "list_installed_environment_packages",
    "list_imported_environment_packages",
    "reset_environment_discovery",
    # Runtime installers
    "install_packages",
]
