from enum import Enum


class AvailableFormats(str, Enum):
    JSON = "json"
    XML = "xml"
    MARKDOWN = "markdown"
    RAW = "raw"
