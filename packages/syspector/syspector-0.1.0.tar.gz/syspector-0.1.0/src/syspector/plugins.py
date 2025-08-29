"""Plugin API: plugins expose a `probe(system_inspector)` callable or entry point."""
from __future__ import annotations

from typing import Protocol, runtime_checkable, Any
import importlib.metadata


@runtime_checkable
class Plugin(Protocol):
    def setup(self, inspector: Any) -> None: ...

def discover_plugins() -> list:
    plugins = []
    for ep in importlib.metadata.entry_points().get("syspector.plugins", []):
        try:
            plugin = ep.load()
            plugins.append(plugin)
        except Exception:
            # avoid crashing the inspector if a plugin is broken
            continue
    return plugins
