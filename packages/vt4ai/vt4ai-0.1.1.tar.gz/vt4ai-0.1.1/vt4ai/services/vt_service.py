"""
VirusTotal service layer; contains all business logic for VT operations.
This layer is shared between REST API and MCP implementations.
"""

from typing import Any, Dict, List, Optional, Union

from vt4ai.client import VT4AIClient
from vt4ai.constants.file_relationships import FileRelationship
from vt4ai.constants.output_formats import AvailableFormats
from vt4ai.templates.templates_loader import TemplateLoader


class VTService:
    """
    Service layer for VirusTotal operations.
    Manages a persistent client connection for improved performance.
    """

    def __init__(self, api_key: str, template_loader: Optional[TemplateLoader] = None):
        """
        Initializes the VTService.

        Args:
            api_key: Your VirusTotal API key.
            template_loader: A template loader object
        """
        self.client = VT4AIClient(api_key, template_loader)

    async def close(self):
        """Closes the underlying VirusTotal client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - automatically closes the client."""
        await self.close()

    async def get_file_report(
        self,
        file_hash: str,
        format: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get file report from VirusTotal."""
        return await self.client.get_file_report_by_hash(file_hash, format, template_name)

    async def get_url_report(
        self,
        url: str,
        format: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get URL report from VirusTotal."""
        return await self.client.get_url_report(url, format, template_name)

    async def get_domain_report(
        self,
        domain: str,
        format: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get domain report from VirusTotal."""
        return await self.client.get_domain_report(domain, format, template_name)

    async def get_ip_report(
        self,
        ip: str,
        format: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get IP report from VirusTotal."""
        return await self.client.get_ip_report(ip, format, template_name)

    async def get_file_report_with_relationships_descriptors(
        self,
        file_hash: str,
        relationship: str,
        format: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get objects related to a file by relationship type."""
        return await self.client.get_file_report_with_relationships_descriptors(
            file_hash=file_hash,
            relationship=relationship,
            template_name=template_name,
            limit=limit,
            cursor=cursor,
            format_enum=format,
        )

    def get_templates_summary(self) -> Dict[str, Any]:
        """Get a summary of all available templates."""
        return self.client.template_loader.get_templates_summary()

    @staticmethod
    def get_relationship_types() -> List[Dict[str, str]]:
        """Get all available file relationship types."""
        descriptions = {
            "behaviours": "Behaviors observed during dynamic analysis",
            "bundled_files": "Files bundled within this file (e.g., in archives)",
            "carbonblack_children": "Child processes spawned (Carbon Black data)",
            "carbonblack_parents": "Parent processes that spawned this file (Carbon Black data)",
            "compressed_parents": "Archive files that contain this file",
            "contacted_domains": "Domains contacted during execution",
            "contacted_ips": "IP addresses contacted during execution",
            "contacted_urls": "URLs contacted during execution",
            "dropped_files": "Files dropped/created during execution",
            "email_attachments": "Email messages that contain this file as attachment",
            "email_parents": "Email messages from which this file was extracted",
            "embedded_domains": "Domains embedded in the file content",
            "embedded_ips": "IP addresses embedded in the file content",
            "embedded_urls": "URLs embedded in the file content",
            "execution_parents": "Files that executed this file",
            "graphs": "Behavior graphs associated with this file",
            "itw_domains": "Domains where this file was found in the wild",
            "itw_ips": "IP addresses where this file was found in the wild",
            "itw_urls": "URLs where this file was found in the wild",
            "overlay_children": "Files that have this file as overlay",
            "overlay_parents": "Files used as overlay for this file",
            "pcap_children": "Network traffic captures related to this file",
            "pcap_parents": "Network traffic captures that contain this file",
            "pe_resource_children": "PE resources contained in this file",
            "pe_resource_parents": "Files that contain this file as PE resource",
            "similar_files": "Files similar to this one",
            "submissions": "Submission information for this file",
        }

        return [
            {
                "value": rel.value,
                "description": descriptions.get(rel.value, f"Objects related by {rel.value}"),
            }
            for rel in FileRelationship
        ]

    @staticmethod
    def validate_relationship_type(relationship: str) -> bool:
        """Validate if relationship type is valid."""
        try:
            FileRelationship(relationship)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_available_formats() -> List[str]:
        """Get all available output formats."""
        return [fmt.value for fmt in AvailableFormats]

    @staticmethod
    def get_available_relationships() -> List[str]:
        """Get all available relationship types."""
        return [rel.value for rel in FileRelationship]
