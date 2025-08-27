import json
from typing import Any, Dict, List, Union


def json_to_markdown(
    data: Union[Dict[str, Any], List[Any], str],
    title: str = None,
    level: int = 1,
) -> str:
    """
    Convert a JSON object to Markdown format recursively. Generic function.

    Args:
        data: JSON data (dict, list, or JSON string)
        title: Optional title for the document
        level: Current heading level (1-6)

    Returns:
        Formatted Markdown string
    """
    # Parse JSON string if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return f"```\n{data}\n```"

    markdown_lines = []

    # Add title if provided
    if title and level == 1:
        markdown_lines.append(f"# {title}\n")

    # Process the data
    markdown_lines.extend(_convert_to_markdown(data, level))

    return "\n".join(markdown_lines)


def _convert_to_markdown(data: Any, level: int = 1) -> List[str]:
    """
    Recursively convert data to markdown lines.

    Args:
        data: Data to convert
        level: Current heading level

    Returns:
        List of markdown lines
    """
    lines = []

    if isinstance(data, dict):
        lines.extend(_dict_to_markdown(data, level))
    elif isinstance(data, list):
        lines.extend(_list_to_markdown(data, level))
    else:
        lines.append(_value_to_markdown(data))

    return lines


def _dict_to_markdown(data: Dict[str, Any], level: int) -> List[str]:
    """Convert dictionary to markdown."""
    lines = []

    for key, value in data.items():
        # Create heading for the key
        heading_level = min(level, 6)  # Maximum heading level is 6
        heading = "#" * heading_level + f" {_format_key(key)}"
        lines.append(heading)
        lines.append("")  # Empty line after heading

        if isinstance(value, dict):
            if not value:  # Empty dict
                lines.append("*No data available*")
                lines.append("")
            else:
                lines.extend(_dict_to_markdown(value, level + 1))
        elif isinstance(value, list):
            if not value:  # Empty list
                lines.append("*No items*")
                lines.append("")
            else:
                lines.extend(_list_to_markdown(value, level + 1))
        else:
            lines.append(_value_to_markdown(value))
            lines.append("")  # Empty line after value

    return lines


def _list_to_markdown(data: List[Any], level: int) -> List[str]:
    """Convert list to markdown."""
    lines = []

    if not data:
        lines.append("*Empty list*")
        return lines

    # Check if all items are simple values (not dict/list)
    all_simple = all(not isinstance(item, (dict, list)) for item in data)

    if all_simple:
        # Simple bullet list
        for item in data:
            lines.append(f"- {_value_to_markdown(item)}")
    else:
        # Complex list with numbered items
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                lines.append(f"**{i}.** ")
                lines.append("")
                # Indent the dictionary content
                dict_lines = _dict_to_markdown(item, level + 1)
                lines.extend(dict_lines)
            elif isinstance(item, list):
                lines.append(f"**{i}.** Nested list:")
                lines.append("")
                nested_lines = _list_to_markdown(item, level + 1)
                # Indent nested list
                lines.extend([f"  {line}" if line else "" for line in nested_lines])
            else:
                lines.append(f"{i}. {_value_to_markdown(item)}")

    lines.append("")  # Empty line after list
    return lines


def _value_to_markdown(value: Any) -> str:
    """Convert a single value to markdown representation."""
    if value is None:
        return "*None*"
    elif isinstance(value, bool):
        return f"**{value}**"
    elif isinstance(value, (int, float)):
        return f"`{value}`"
    elif isinstance(value, str):
        if not value.strip():
            return "*Empty string*"
        # Check if it looks like a URL
        if value.startswith(("http://", "https://", "ftp://")):
            return f"[{value}]({value})"
        # Check if it contains newlines (multiline text)
        elif "\n" in value:
            return f"```\n{value}\n```"
        # Regular string
        else:
            return value
    else:
        return f"`{str(value)}`"


def _format_key(key: str) -> str:
    """Format dictionary keys for better readability."""
    # Replace underscores with spaces and capitalize words
    formatted = key.replace("_", " ").title()

    # Handle common abbreviations
    abbreviations = {
        "Id": "ID",
        "Url": "URL",
        "Api": "API",
        "Http": "HTTP",
        "Https": "HTTPS",
        "Ip": "IP",
        "Dns": "DNS",
        "Tcp": "TCP",
        "Udp": "UDP",
        "Sha256": "SHA256",
        "Sha1": "SHA1",
        "Md5": "MD5",
        "Pe": "PE",
        "C2": "C2",
        "Av": "AV",
    }

    for old, new in abbreviations.items():
        formatted = formatted.replace(old, new)

    return formatted


def dict_to_table(data: Dict[str, Any], max_depth: int = 1) -> str:
    """
    Convert a flat dictionary to a markdown table.

    Args:
        data: Dictionary to convert
        max_depth: Maximum depth to flatten nested structures

    Returns:
        Markdown table string
    """
    if not isinstance(data, dict) or not data:
        return "*No data to display in table format*"

    # Flatten nested dictionaries up to max_depth
    flattened = _flatten_dict(data, max_depth=max_depth)

    # Create table
    lines = []
    lines.append("| Key | Value |")
    lines.append("|-----|-------|")

    for key, value in flattened.items():
        formatted_key = _format_key(key)
        formatted_value = _value_to_markdown(value).replace("\n", "<br>")
        lines.append(f"| {formatted_key} | {formatted_value} |")

    return "\n".join(lines)


def _flatten_dict(
    data: Dict[str, Any],
    prefix: str = "",
    max_depth: int = 1,
    current_depth: int = 0,
) -> Dict[str, Any]:
    """Flatten nested dictionary with depth limit."""
    items = {}

    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict) and current_depth < max_depth:
            items.update(_flatten_dict(value, new_key, max_depth, current_depth + 1))
        else:
            items[new_key] = value

    return items


def list_to_table(data: List[Dict[str, Any]], max_columns: int = 10) -> str:
    """
    Convert a list of dictionaries to a markdown table.

    Args:
        data: List of dictionaries
        max_columns: Maximum number of columns to include

    Returns:
        Markdown table string
    """
    if not isinstance(data, list) or not data:
        return "*No data to display in table format*"

    # Get all unique keys from all dictionaries
    all_keys = set()
    for item in data:
        if isinstance(item, dict):
            all_keys.update(item.keys())

    # Limit columns
    columns = sorted(list(all_keys))[:max_columns]

    if not columns:
        return "*No valid data for table format*"

    # Create table header
    lines = []
    header = "| " + " | ".join(_format_key(col) for col in columns) + " |"
    separator = "|" + "|".join("-----" for _ in columns) + "|"

    lines.append(header)
    lines.append(separator)

    # Add rows
    for item in data:
        if isinstance(item, dict):
            row_values = []
            for col in columns:
                value = item.get(col, "")
                formatted_value = _value_to_markdown(value).replace("\n", "<br>")
                row_values.append(formatted_value)

            row = "| " + " | ".join(row_values) + " |"
            lines.append(row)

    return "\n".join(lines)
