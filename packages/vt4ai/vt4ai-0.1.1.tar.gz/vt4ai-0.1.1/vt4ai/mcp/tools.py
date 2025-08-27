"""
MCP Tools for VT4AI - VirusTotal analysis tools.
"""

import json
from typing import Optional

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from vt4ai.constants.output_formats import AvailableFormats
from vt4ai.mcp.config import get_api_key
from vt4ai.services.vt_service import VTService
from vt4ai.templates.templates_loader import TemplateLoader


### Refactor: register tools by category
def register_tools(mcp: FastMCP) -> None:
    """
    Register all VT4AI tools with the FastMCP server.
    Each tool creates its own VTService instance with proper async context management.
    """
    try:
        api_key = get_api_key()
        # Start the template loader in order to avoid the load on each tool call
        shared_template_loader = TemplateLoader()
    except Exception as e:
        print(f"FATAL: Could not get API key for MCP tools. Error: {e}")
        return

    @mcp.tool()
    async def vt_get_file_report(
        file_hash: str,
        format: str = "json",
        template_name: Optional[str] = None,
        ctx: Context[ServerSession, None] = None,
    ) -> str:
        """
        Get a file report from VirusTotal by hash.

        Args:
            file_hash: File hash (MD5, SHA1, or SHA256)
            format: Output format (json, markdown, xml, raw)
            template_name: Name of the template to apply for filtering (use get_available_templates to see options)

        Returns:
            Processed file analysis report
        """
        try:
            format_enum = AvailableFormats(format)
            if ctx:
                await ctx.info(f"Analyzing file hash: {file_hash}")

            async with VTService(api_key, shared_template_loader) as service:
                result = await service.get_file_report(file_hash, format_enum, template_name)

            if ctx:
                await ctx.info("File analysis completed successfully")

            # Ensure result is always a string for MCP tools
            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            if ctx:
                await ctx.error(f"Error analyzing file: {str(e)}")
            raise

    @mcp.tool()
    async def vt_get_url_report(
        url: str,
        format: str = "json",
        template_name: Optional[str] = None,
        ctx: Context[ServerSession, None] = None,
    ) -> str:
        """
        Get a URL report from VirusTotal.

        Args:
            url: URL to analyze
            format: Output format (json, markdown, xml, raw)

        Returns:
            Processed URL analysis report
        """
        try:
            format_enum = AvailableFormats(format)
            if ctx:
                await ctx.info(f"Analyzing URL: {url}")

            async with VTService(api_key, shared_template_loader) as service:
                result = await service.get_url_report(url, format_enum, template_name)

            if ctx:
                await ctx.info("URL analysis completed successfully")

            # Ensure result is always a string for MCP tools
            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            if ctx:
                await ctx.error(f"Error analyzing URL: {str(e)}")
            raise

    @mcp.tool()
    async def vt_get_domain_report(
        domain: str,
        format: str = "json",
        template_name: Optional[str] = None,
        ctx: Context[ServerSession, None] = None,
    ) -> str:
        """
        Get a domain report from VirusTotal.

        Args:
            domain: Domain name to analyze
            format: Output format (json, markdown, xml, raw)
            template_name: Name of the template to apply for filtering (use get_available_templates to see options)

        Returns:
            Processed domain analysis report
        """
        try:
            format_enum = AvailableFormats(format)
            if ctx:
                await ctx.info(f"Analyzing domain: {domain}")

            async with VTService(api_key, shared_template_loader) as service:
                result = await service.get_domain_report(domain, format_enum, template_name)

            if ctx:
                await ctx.info("Domain analysis completed successfully")

            # Ensure result is always a string for MCP tool
            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            if ctx:
                await ctx.error(f"Error analyzing domain: {str(e)}")
            raise

    @mcp.tool()
    async def vt_get_ip_report(
        ip: str,
        format: str = "json",
        template_name: Optional[str] = None,
        ctx: Context[ServerSession, None] = None,
    ) -> str:
        """
        Get an IP address report from VirusTotal.

        Args:
            ip: IP address to analyze (IPv4 or IPv6)
            format: Output format (json, markdown, xml, raw)
            template_name: Name of the template to apply for filtering (use get_available_templates to see options)

        Returns:
            Processed IP analysis report
        """
        try:
            format_enum = AvailableFormats(format)
            if ctx:
                await ctx.info(f"Analyzing IP: {ip}")

            async with VTService(api_key, shared_template_loader) as service:
                result = await service.get_ip_report(ip, format_enum, template_name)

            if ctx:
                await ctx.info("IP analysis completed successfully")

            # Ensure result is always a string for MCP tools
            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            if ctx:
                await ctx.error(f"Error analyzing IP: {str(e)}")
            raise

    @mcp.tool()
    async def vt_get_file_report_with_relationships(
        file_hash: str,
        relationship: str,
        format: str = "json",
        template_name: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[str] = None,
        ctx: Context[ServerSession, None] = None,
    ) -> str:
        """
        Get a file report including related objects by relationship type.

        Args:
            file_hash: File hash (MD5, SHA1, or SHA256)
            relationship: Type of relationship (use get_relationship_types to see available options)
            format: Output format (json, markdown, xml, raw) for the report.
            template_name: Name of the template to apply for filtering the main file attributes.
            limit: Maximum number of related objects to return (default: 10).
            cursor: Pagination cursor for continued results.

        Returns:
            A report containing file attributes and related objects data.
        """
        try:
            format_enum = AvailableFormats(format)
            if ctx:
                await ctx.info(f"Getting {relationship} relationships for file: {file_hash}")

            async with VTService(api_key, shared_template_loader) as service:
                result = await service.get_file_report_with_relationships_descriptors(
                    file_hash=file_hash,
                    relationship=relationship,
                    format=format_enum,
                    template_name=template_name,
                    limit=limit,
                    cursor=cursor,
                )

            if ctx:
                await ctx.info(f"Retrieved {relationship} relationships successfully")

            # Ensure result is always a string for MCP tools
            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            if ctx:
                await ctx.error(f"Error getting file relationships: {str(e)}")
            raise

    @mcp.tool()
    def vt_get_relationship_types() -> str:
        """
        Get all available file relationship types.

        Returns:
            List of available relationship types with descriptions
        """
        relationships = VTService.get_relationship_types()
        formatted = "Available File Relationship Types:\n\n"
        for rel in relationships:
            formatted += f"• {rel['value']}: {rel['description']}\n"
        return formatted

    @mcp.tool()
    def get_available_formats() -> str:
        """
        Get all available output formats.

        Returns:
            List of supported output formats
        """
        formats = VTService.get_available_formats()
        descriptions = {
            "json": "Structured JSON format (default) - optimized for AI processing",
            "markdown": "Human-readable Markdown format",
            "xml": "XML format for structured data exchange",
            "raw": "Raw VirusTotal API response",
        }
        formatted = "Available Output Formats:\n\n"
        for fmt in formats:
            desc = descriptions.get(fmt, "Standard format")
            formatted += f"• {fmt}: {desc}\n"
        return formatted

    @mcp.tool()
    def get_available_templates() -> str:
        """
        Get a summary of available templates for filtering analysis results.

        Returns:
            A summary of available templates, grouped by object type.
        """
        # Create a temporary service instance for template access
        temp_service = VTService(api_key, shared_template_loader)
        summary = temp_service.get_templates_summary()
        formatted_output = "Available Templates:\n"
        for object_type, templates in summary.items():
            formatted_output += f"\n## {object_type.title()} Templates\n"
            if not templates:
                formatted_output += "- No templates available.\n"
            else:
                for template in templates:
                    name = template.get("name", "N/A")
                    description = template.get("description", "No description available.")
                    formatted_output += f"- **{name}**: {description}\n"
        return formatted_output
