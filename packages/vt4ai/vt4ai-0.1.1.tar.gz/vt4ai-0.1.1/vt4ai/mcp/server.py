"""
VT4AI MCP Server implementation using FastMCP.
Provides VirusTotal analysis tools for AI agents via Model Context Protocol.
"""

from mcp.server.fastmcp import FastMCP

from vt4ai.mcp.config import (
    configure_logging,
    print_startup_message,
    setup_argument_parser,
)
from vt4ai.mcp.prompts import register_prompts
from vt4ai.mcp.tools import register_tools


def create_server() -> FastMCP:
    """Create and configure the FastMCP server with all components."""

    mcp = FastMCP(
        name="VT4AI",
        instructions="VirusTotal analysis tools for AI agents. Provides file, URL, domain, and IP analysis capabilities.",
    )

    register_tools(mcp)
    register_prompts(mcp)

    return mcp


def main():
    """Main entry point with argument parsing."""

    parser = setup_argument_parser()
    args = parser.parse_args()

    configure_logging(args.debug)

    print_startup_message(args.transport)

    mcp = create_server()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
