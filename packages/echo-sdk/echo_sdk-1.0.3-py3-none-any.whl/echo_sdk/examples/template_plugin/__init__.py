"""Template plugin for Echo multi-agent system.

This template demonstrates how to create a Echo plugin using the SDK.
Auto-registers the plugin when imported.
"""

from echo_sdk import register_plugin

from .plugin import TemplatePlugin

register_plugin(TemplatePlugin)
