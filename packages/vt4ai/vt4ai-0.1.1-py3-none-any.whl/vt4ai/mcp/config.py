"""
Configuration and utilities for VT4AI MCP Server.
"""

import argparse
import logging
import os
import sys


def get_api_key() -> str:
    """Get API key from environment variable."""
    api_key = os.getenv("VT4AI_API_KEY")
    if not api_key:
        raise ValueError("VT4AI_API_KEY environment variable is required")
    return api_key


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="VT4AI MCP Server - VirusTotal analysis tools for AI agents",
        prog="python -m vt4ai.mcp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport options:
  stdio           Standard input/output
  streamable-http HTTP transport

Examples:
  python -m vt4ai.mcp                          # Use stdio transport
  python -m vt4ai.mcp --transport stdio       # Use stdio transport (explicit)
  python -m vt4ai.mcp -t streamable-http      # Use HTTP transport

Environment:
  VT4AI_API_KEY   VirusTotal API key (required)
        """,
    )

    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


def configure_logging(debug: bool = False) -> None:
    """Configure logging based on debug flag."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)


def print_startup_message(transport: str) -> None:
    """Print startup message to stderr."""
    print(f"Starting VT4AI MCP Server with {transport} transport", file=sys.stderr)

    if transport == "streamable-http":
        print(
            "Server will be available at: http://localhost:8000/mcp",
            file=sys.stderr,
        )
