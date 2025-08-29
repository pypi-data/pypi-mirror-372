"""syspector package entrypoints."""
__version__ = "0.1.0"

from .core import SystemInspector
from .api import create_app
from .cli import main

__all__ = ["SystemInspector", "create_app", "main"]
