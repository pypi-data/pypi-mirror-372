"""
Email Template Review MCP Server

A Model Context Protocol server for automated email template review and management.
"""

__version__ = "1.1.1"

def get_main():
    """Lazy import to avoid environment variable requirements during package import."""
    from .server import main
    return main

__all__ = ["get_main", "__version__"]