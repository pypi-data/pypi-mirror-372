from typing import Any, Dict, List, Optional, Union

import vt

from vt4ai.constants.file_relationships import FileRelationship
from vt4ai.constants.output_formats import AvailableFormats
from vt4ai.filters.object_attributes_filter import AttributesFilter
from vt4ai.templates.templates_loader import TemplateLoader
from vt4ai.utils.json2md import json_to_markdown
from vt4ai.utils.json2xml import json_to_xml


class VT4AIClient:
    def __init__(self, api_key: str, template_loader: Optional[TemplateLoader] = None):
        self.api_key = api_key
        self.client = vt.Client(apikey=api_key)
        self.template_loader = template_loader if template_loader else TemplateLoader()
        self.attributes_filter = AttributesFilter()

    async def close(self):
        """Close the VirusTotal client connection."""
        if self.client:
            await self.client.close_async()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - automatically closes the client."""
        await self.close()

    def _get_templates_to_apply(
        self, object_type: str, template_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the templates to be applied based on the object type and an optional template name.
        """
        templates_to_apply = []
        all_templates = self.template_loader.get_templates_for_object(object_type)

        if template_name:
            template = next(
                (t for t in all_templates if t.get("name") == template_name),
                None,
            )
            if template:
                templates_to_apply.append(template)
            else:
                print(
                    f"Warning: Template '{template_name}' not found for object type '{object_type}'."
                )
        else:
            templates_to_apply = all_templates

        return templates_to_apply

    async def _get_generic_report(
        self,
        api_path: str,
        object_type: str,
        identifier: str,
        report_title: str,
        root_name: str,
        format_enum: AvailableFormats,
        template_name: Optional[str],
    ) -> Union[Dict[str, Any], str]:
        """
        A generic method to fetch, filter, and format a VirusTotal report.
        """
        if format_enum not in AvailableFormats:
            raise ValueError(
                f"Invalid format: {format_enum}. Available formats: {AvailableFormats}"
            )

        vt_raw_object: vt.Object = await self.client.get_object_async(api_path)
        vt_raw_attributes = vt_raw_object.to_dict()["attributes"]

        if format_enum == AvailableFormats.RAW:
            return vt_raw_attributes

        templates = self._get_templates_to_apply(object_type, template_name)
        filtered_attributes = self.attributes_filter.filter_attributes(
            attributes=vt_raw_attributes, templates=templates
        )

        if format_enum == AvailableFormats.JSON:
            return filtered_attributes
        elif format_enum == AvailableFormats.MARKDOWN:
            return json_to_markdown(filtered_attributes, title=f"{report_title}: {identifier}")
        elif format_enum == AvailableFormats.XML:
            return json_to_xml(filtered_attributes, root_name=root_name)

        return filtered_attributes

    async def get_file_report_by_hash(
        self,
        hash_id: str,
        format_enum: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get the file report by hash."""
        return await self._get_generic_report(
            api_path=f"/files/{hash_id}",
            object_type="file",
            identifier=hash_id,
            report_title="File Report",
            root_name="file_report",
            format_enum=format_enum,
            template_name=template_name,
        )

    async def get_domain_report(
        self,
        domain: str,
        format_enum: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get the domain report."""
        return await self._get_generic_report(
            api_path=f"/domains/{domain}",
            object_type="domain",
            identifier=domain,
            report_title="Domain Report",
            root_name="domain_report",
            format_enum=format_enum,
            template_name=template_name,
        )

    async def get_ip_report(
        self,
        ip_address: str,
        format_enum: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get the IP address report."""
        return await self._get_generic_report(
            api_path=f"/ip_addresses/{ip_address}",
            object_type="ip",  # Matches the template's object type
            identifier=ip_address,
            report_title="IP Address Report",
            root_name="ip_report",
            format_enum=format_enum,
            template_name=template_name,
        )

    async def get_url_report(
        self,
        url: str,
        format_enum: AvailableFormats = AvailableFormats.JSON,
        template_name: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Get the url report."""
        url_id = vt.url_id(url)
        return await self._get_generic_report(
            api_path=f"/urls/{url_id}",
            object_type="url",  # Matches the template's object type
            identifier=url_id,
            report_title="URL Report",
            root_name="url_report",
            format_enum=format_enum,
            template_name=template_name,
        )

    ### TODO: Needs refactor
    async def get_file_report_with_relationships_descriptors(
        self,
        file_hash: str,
        relationship: str,
        template_name: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[str] = None,
        format_enum: AvailableFormats = AvailableFormats.JSON,
    ):
        if format_enum not in AvailableFormats:
            raise ValueError(
                f"Invalid format: {format_enum}. Available formats: {AvailableFormats}"
            )

        try:
            FileRelationship(relationship)
        except ValueError:
            raise ValueError(
                f"Invalid relationship: {relationship}. Available formats: {[r.value for r in FileRelationship]}"
            )

        api_path = f"/files/{file_hash}?relationships={relationship}&limit={limit}"
        if cursor:
            api_path = f"{api_path}&cursor={cursor}"

        print(api_path)

        vt_raw_object: vt.Object = await self.client.get_object_async(api_path)
        vt_raw_object_dict = vt_raw_object.to_dict()
        vt_raw_attributes = vt_raw_object_dict["attributes"]
        relationships = vt_raw_object_dict["relationships"]

        if format_enum == AvailableFormats.RAW:
            return vt_raw_object_dict

        templates = self._get_templates_to_apply("file", template_name)
        filtered_attributes = self.attributes_filter.filter_attributes(
            attributes=vt_raw_attributes, templates=templates
        )

        file_attributes_with_relationships = {}
        file_attributes_with_relationships["attributes"] = filtered_attributes
        file_attributes_with_relationships["relationships"] = relationships

        if format_enum == AvailableFormats.JSON:
            return file_attributes_with_relationships
        elif format_enum == AvailableFormats.MARKDOWN:
            return json_to_markdown(
                file_attributes_with_relationships, title=f"{file_hash}: {relationship}"
            )
        elif format_enum == AvailableFormats.XML:
            return json_to_xml(
                file_attributes_with_relationships, root_name=f"{file_hash}:{relationship}"
            )

        return file_attributes_with_relationships
