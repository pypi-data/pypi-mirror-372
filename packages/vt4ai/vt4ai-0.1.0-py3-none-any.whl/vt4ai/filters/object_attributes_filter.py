import copy
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AttributesFilter:
    """
    A class to filter object attributes based on templates
    """

    @staticmethod
    def _apply_filter(current_obj: Any, pattern_parts: List[str]):
        """
        Recursively navigates through a nested dictionary and removes keys
        based on a given pattern.

        The pattern is provided as a list of keys (e.g.,
        ['last_analysis_results', '*', 'category']).

        Args:
            current_obj: The current dictionary or sub-dictionary being processed.
            pattern_parts: A list of strings representing the path to the key
                           to be removed. Can include '*' as a wildcard.
        """
        if not pattern_parts or not isinstance(current_obj, dict):
            return

        key = pattern_parts[0]
        remaining_parts = pattern_parts[1:]

        if key == "*":
            for sub_obj in current_obj.values():
                AttributesFilter._apply_filter(sub_obj, remaining_parts)
            return

        # If the key is a specific name and it exists in the current object.
        if key in current_obj:
            if not remaining_parts:
                # If this is the last part of the pattern, we have found the target key to delete.
                logger.debug(f"Removing field '{key}' based on pattern.")
                del current_obj[key]
            else:
                AttributesFilter._apply_filter(current_obj[key], remaining_parts)

    @staticmethod
    def filter_attributes(
        attributes: Dict[str, Any], templates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Filters the attributes of an object based on a list of templates.

        This method supports complex exclusion patterns with wildcards to
        remove fields from nested dictionaries. For example, the pattern
        'last_analysis_results.*.category' will remove the 'category' field
        from every entry within the 'last_analysis_results' dictionary.

        Args:
            attributes: The dictionary of attributes to be filtered.
            templates: A list of template dictionaries, each potentially
                       containing an 'exclude_fields' list.

        Returns:
            A new dictionary containing the filtered attributes. The original
            dictionary is not modified.
        """
        # Use a copy to ensure the original attributes dictionary is not mutated.
        filtered_attributes = copy.deepcopy(attributes)

        if not templates:
            logger.info("No templates provided for filtering. Returning original attributes.")
            return filtered_attributes

        # Collect all unique exclusion patterns from all templates.
        all_exclude_fields = set()
        for template in templates:
            exclude_fields = template.get("exclude_fields", [])
            if isinstance(exclude_fields, list):
                all_exclude_fields.update(exclude_fields)
            else:
                logger.warning(
                    f"Template '{template.get('name', 'N/A')}' has a "
                    f"non-list 'exclude_fields' value. Skipping."
                )

        if not all_exclude_fields:
            return filtered_attributes

        logger.debug(f"Excluding fields based on patterns: {all_exclude_fields}")

        # Apply each exclusion pattern to the attributes.
        for pattern in all_exclude_fields:
            pattern_parts = pattern.split(".")
            AttributesFilter._apply_filter(filtered_attributes, pattern_parts)

        return filtered_attributes
