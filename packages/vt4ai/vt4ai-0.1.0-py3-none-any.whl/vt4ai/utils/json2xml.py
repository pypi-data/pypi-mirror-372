import json
import re
from typing import Any, Dict, List, Union
from xml.sax.saxutils import escape


def json_to_xml(
    data: Union[Dict[str, Any], List[Any], str],
    root_name: str = "root",
    pretty: bool = True,
) -> str:
    """
    Convert a JSON object to XML format recursively. Generic function.

    Args:
        data: JSON data (dict, list, or JSON string)
        root_name: Name for the root XML element
        pretty: Whether to format with indentation

    Returns:
        Formatted XML string
    """
    # Parse JSON string if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            # If it's not valid JSON, treat as plain text
            return (
                f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_name}>{escape(data)}</{root_name}>'
            )

    # Start building XML
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']

    # Convert data to XML elements
    xml_content = _convert_to_xml(data, root_name, 0 if pretty else -1)
    xml_lines.extend(xml_content)

    return "\n".join(xml_lines) if pretty else "".join(xml_lines)


def _convert_to_xml(data: Any, element_name: str, indent_level: int = 0) -> List[str]:
    """
    Recursively convert data to XML elements.

    Args:
        data: Data to convert
        element_name: Name for the XML element
        indent_level: Current indentation level (-1 for no formatting)

    Returns:
        List of XML lines
    """
    lines = []
    indent = "  " * indent_level if indent_level >= 0 else ""

    # Sanitize element name
    clean_name = _sanitize_element_name(element_name)

    if isinstance(data, dict):
        lines.extend(_dict_to_xml(data, clean_name, indent_level))
    elif isinstance(data, list):
        lines.extend(_list_to_xml(data, clean_name, indent_level))
    else:
        # Simple value
        value_str = _value_to_xml_string(data)
        if indent_level >= 0:
            lines.append(f"{indent}<{clean_name}>{value_str}</{clean_name}>")
        else:
            lines.append(f"<{clean_name}>{value_str}</{clean_name}>")

    return lines


def _dict_to_xml(data: Dict[str, Any], element_name: str, indent_level: int) -> List[str]:
    """Convert dictionary to XML elements."""
    lines = []
    indent = "  " * indent_level if indent_level >= 0 else ""

    if not data:
        # Empty dictionary
        if indent_level >= 0:
            lines.append(f"{indent}<{element_name}/>")
        else:
            lines.append(f"<{element_name}/>")
        return lines

    # Opening tag
    if indent_level >= 0:
        lines.append(f"{indent}<{element_name}>")
    else:
        lines.append(f"<{element_name}>")

    # Process each key-value pair
    for key, value in data.items():
        child_lines = _convert_to_xml(value, key, indent_level + 1 if indent_level >= 0 else -1)
        lines.extend(child_lines)

    # Closing tag
    if indent_level >= 0:
        lines.append(f"{indent}</{element_name}>")
    else:
        lines.append(f"</{element_name}>")

    return lines


def _list_to_xml(data: List[Any], element_name: str, indent_level: int) -> List[str]:
    """Convert list to XML elements."""
    lines = []
    indent = "  " * indent_level if indent_level >= 0 else ""

    if not data:
        # Empty list
        if indent_level >= 0:
            lines.append(f"{indent}<{element_name}/>")
        else:
            lines.append(f"<{element_name}/>")
        return lines

    # Opening tag for the list container
    if indent_level >= 0:
        lines.append(f"{indent}<{element_name}>")
    else:
        lines.append(f"<{element_name}>")

    # Process each item in the list
    for i, item in enumerate(data):
        # Use 'item' as the element name for list items, with index as attribute
        item_element_name = "item"

        if isinstance(item, dict):
            # For dictionary items, use the container with index
            item_lines = _dict_to_xml(
                item,
                item_element_name,
                indent_level + 1 if indent_level >= 0 else -1,
            )
            # Add index attribute to the first line
            if item_lines and indent_level >= 0:
                first_line = item_lines[0]
                # Insert index attribute
                tag_end = first_line.find(">")
                if tag_end > 0:
                    item_lines[0] = first_line[:tag_end] + f' index="{i}"' + first_line[tag_end:]
        elif isinstance(item, list):
            # Nested list
            item_lines = _list_to_xml(
                item,
                f"{item_element_name}_list",
                indent_level + 1 if indent_level >= 0 else -1,
            )
            if item_lines and indent_level >= 0:
                first_line = item_lines[0]
                tag_end = first_line.find(">")
                if tag_end > 0:
                    item_lines[0] = first_line[:tag_end] + f' index="{i}"' + first_line[tag_end:]
        else:
            # Simple value
            value_str = _value_to_xml_string(item)
            if indent_level >= 0:
                item_indent = "  " * (indent_level + 1)
                item_lines = [
                    f'{item_indent}<{item_element_name} index="{i}">{value_str}</{item_element_name}>'
                ]
            else:
                item_lines = [f'<{item_element_name} index="{i}">{value_str}</{item_element_name}>']

        lines.extend(item_lines)

    # Closing tag for the list container
    if indent_level >= 0:
        lines.append(f"{indent}</{element_name}>")
    else:
        lines.append(f"</{element_name}>")

    return lines


def _value_to_xml_string(value: Any) -> str:
    """Convert a single value to XML-safe string representation."""
    if value is None:
        return ""
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Escape XML special characters
        return escape(value)
    else:
        return escape(str(value))


def _sanitize_element_name(name: str) -> str:
    """Sanitize string to be a valid XML element name."""
    # XML element names must start with a letter or underscore
    # and can contain letters, digits, hyphens, underscores, and periods

    # Replace spaces and invalid characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", str(name))

    # Ensure it starts with a letter or underscore
    if sanitized and not re.match(r"^[a-zA-Z_]", sanitized):
        sanitized = f"item_{sanitized}"

    # Handle empty or invalid names
    if not sanitized:
        sanitized = "item"

    # Ensure it's not too long (practical limit)
    if len(sanitized) > 50:
        sanitized = sanitized[:47] + "..."

    return sanitized


def dict_to_xml_attributes(data: Dict[str, Any], element_name: str = "item") -> str:
    """
    Convert a flat dictionary to XML element with attributes.

    Args:
        data: Dictionary to convert (should contain simple values only)
        element_name: Name for the XML element

    Returns:
        XML element string with attributes
    """
    if not isinstance(data, dict) or not data:
        return f"<{element_name}/>"

    attributes = []
    content = []

    for key, value in data.items():
        clean_key = _sanitize_element_name(key)

        # Simple values become attributes, complex values become content
        if isinstance(value, (str, int, float, bool)) and value is not None:
            if isinstance(value, str) and len(value) < 100:  # Short strings as attributes
                attr_value = escape(str(value)).replace('"', "&quot;")
                attributes.append(f'{clean_key}="{attr_value}"')
            else:
                content.append(f"<{clean_key}>{_value_to_xml_string(value)}</{clean_key}>")
        else:
            # Complex values go into content
            if isinstance(value, dict):
                content.extend(_dict_to_xml(value, clean_key, 1))
            elif isinstance(value, list):
                content.extend(_list_to_xml(value, clean_key, 1))
            else:
                content.append(f"<{clean_key}>{_value_to_xml_string(value)}</{clean_key}>")

    # Build the element
    attr_string = " " + " ".join(attributes) if attributes else ""

    if content:
        xml_parts = [f"<{element_name}{attr_string}>"]
        xml_parts.extend(content)
        xml_parts.append(f"</{element_name}>")
        return "\n".join(xml_parts)
    else:
        return f"<{element_name}{attr_string}/>"


def list_to_xml_collection(
    data: List[Any],
    collection_name: str = "collection",
    item_name: str = "item",
) -> str:
    """
    Convert a list to XML collection with named items.

    Args:
        data: List to convert
        collection_name: Name for the collection container
        item_name: Name for individual items

    Returns:
        XML collection string
    """
    if not isinstance(data, list):
        return f"<{collection_name}/>"

    if not data:
        return f"<{collection_name}/>"

    lines = [f"<{collection_name}>"]

    for i, item in enumerate(data):
        if isinstance(item, dict):
            # Convert dict to element with attributes
            item_xml = dict_to_xml_attributes(item, item_name)
            # Add index to the first line
            if item_xml.startswith(f"<{item_name}"):
                first_line_end = item_xml.find(">")
                if first_line_end > 0:
                    item_xml = (
                        item_xml[:first_line_end] + f' index="{i}"' + item_xml[first_line_end:]
                    )
            lines.append(f"  {item_xml}")
        else:
            # Simple value
            value_str = _value_to_xml_string(item)
            lines.append(f'  <{item_name} index="{i}">{value_str}</{item_name}>')

    lines.append(f"</{collection_name}>")
    return "\n".join(lines)
