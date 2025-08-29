"""
Entry point for running the MCP server as a module.
"""

if __name__ == "__main__":
    from .server import cli
    cli()