"""
OSINTBuddy 🕵️ – A Plugin-Based Framework for Open Source Intelligence.

This is the root module of the OSINTBuddy package. It provides centralized
access to the plugin system and core APIs for building, loading, and
managing OSINTBuddy plugins.

This module exposes the following public objects:

- `Registry`: Tracks and resolves all registered plugins.
- `Plugin`: Base class for defining OSINT plugins.
- `Use`: Context object passed to plugin transforms.
- `transform`: Decorator for defining plugin transform actions.
- `load_plugin`: Dynamically loads a plugin from code.
- `load_plugins`: Discovers and loads all plugin modules from a directory.

Examples
--------
>>> from osintbuddy import Plugin, transform, Registry
>>> class MyPlugin(Plugin):
...     label = "IP Lookup"
...     entity = [...]
...
...     @transform(label="To ASN", icon="trace")
...     async def transform_asn(self, node, use):
...         return [{"label": "ASN123"}]

Notes
-----
- OSINTBuddy is modular, stateless, and entirely local/offline.
- All plugins are defined using class-based blueprints and exposed as microservices.

Version
-------
0.2.0
"""

import osintbuddy.plugins

__version__ = "0.2.0"

# Explicitly assign public API for static analyzers like Pylance
Registry = osintbuddy.plugins.OBRegistry
Plugin = osintbuddy.plugins.OBPlugin
Use = osintbuddy.plugins.OBUse
transform = osintbuddy.plugins.transform
load_plugin = osintbuddy.plugins.load_plugin
load_plugins = osintbuddy.plugins.load_plugins

__all__ = [
    "Registry",
    "Plugin",
    "Use",
    "transform",
    "load_plugin",
    "load_plugins",
    "__version__",
]
