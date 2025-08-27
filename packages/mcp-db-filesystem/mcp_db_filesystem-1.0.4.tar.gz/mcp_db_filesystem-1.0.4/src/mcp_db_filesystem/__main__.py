#!/usr/bin/env python3
"""
MCP Database Filesystem - Main Entry Point
===========================================

This file allows the package to be executed via `python -m mcp_db_filesystem`.

Usage:
  python -m mcp_db_filesystem        # Start MCP server
  python -m mcp_db_filesystem version # Show version
"""

import argparse
import asyncio
import sys
import warnings


# Suppress asyncio ResourceWarning on Windows
if sys.platform == "win32":
    warnings.filterwarnings(
        "ignore", category=ResourceWarning, message=".*unclosed transport.*"
    )
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")

    # Set asyncio event loop policy to reduce warnings
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        pass


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MCP Database Filesystem - Simple and efficient MCP server for database and filesystem access"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Server command (default)
    subparsers.add_parser("server", help="Start MCP server (default)")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    # Handle commands
    if args.command == "version":
        show_version()
    elif args.command == "server" or args.command is None:
        run_server()
    else:
        parser.print_help()
        sys.exit(1)


def run_server():
    """Start MCP server"""
    from .server import main as server_main
    return asyncio.run(server_main())


def show_version():
    """Show version information"""
    from . import __author__, __version__

    print(f"MCP Database Filesystem v{__version__}")
    print(f"Author: {__author__}")
    print("GitHub: https://github.com/ppengit/mcp-db-filesystem")


if __name__ == "__main__":
    main()
