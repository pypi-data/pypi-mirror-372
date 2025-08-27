"""
FastAPI server module for serving course data via HTTP API.
"""

from .app import create_app
from .cli import cli, main

__all__ = ["create_app", "cli", "main"]