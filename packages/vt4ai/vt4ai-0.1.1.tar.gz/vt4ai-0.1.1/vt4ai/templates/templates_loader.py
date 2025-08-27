import json
import logging
from pathlib import Path
from typing import Any, Dict

_DEFAULT_PATH: Path = Path(__file__).parent

logger = logging.getLogger(__name__)


class TemplateLoader:
    def __init__(self, template_path: Path = _DEFAULT_PATH):
        loaded_templates = {}

        if not template_path.exists() or not template_path.is_dir():
            raise Exception("Error loading templates: The provided path is not a valid directory.")

        logger.info(f"Loading templates from path: {template_path}")

        for template in template_path.glob("**/*.json"):
            try:
                logger.debug(f"Loading the template {template}")
                dict_template = json.loads(template.read_text())
                target_object = dict_template["object"]
                loaded_templates.setdefault(target_object, []).append(dict_template)
                logger.info(f"Loaded template {dict_template['name']} for object {target_object}")
            except Exception as e:
                logger.error(f"Error loading template file {template.name}: {e}")

        self.loaded_templates = loaded_templates

    def get_templates_summary(self) -> dict:
        summary = {}
        for object_type, templates in self.loaded_templates.items():
            summary[object_type] = [
                {
                    "name": t.get("name", "N/A"),
                    "description": t.get("description", "No description available."),
                }
                for t in templates
            ]
        return summary

    def get_templates_for_object(self, object_type: str) -> list:
        return self.loaded_templates.get(object_type, [])

    def get_template_for_object_by_name(self, object_type: str, template_name: Dict[str, Any]):
        templates_for_object = self.get_templates_for_object()
        templates_with_the_name = [
            template["name"] == template_name for template in templates_for_object
        ]

        return templates_with_the_name
