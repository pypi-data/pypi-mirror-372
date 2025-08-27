"""
VirusTotal File Relationships

All possible file relationships in VirusTotal.
"""

from enum import Enum


class FileRelationship(str, Enum):
    """All possible VirusTotal file relationships"""

    # Everyone tier - Available to all users
    BEHAVIOURS = "behaviours"
    BUNDLED_FILES = "bundled_files"
    COLLECTIONS = "collections"
    COMMENTS = "comments"
    CONTACTED_DOMAINS = "contacted_domains"
    CONTACTED_IPS = "contacted_ips"
    CONTACTED_URLS = "contacted_urls"
    DROPPED_FILES = "dropped_files"
    EXECUTION_PARENTS = "execution_parents"
    GRAPHS = "graphs"
    PE_RESOURCE_CHILDREN = "pe_resource_children"
    PE_RESOURCE_PARENTS = "pe_resource_parents"
    VOTES = "votes"

    # Enterprise tier - VT Enterprise users only
    ANALYSES = "analyses"
    CARBONBLACK_CHILDREN = "carbonblack_children"
    CARBONBLACK_PARENTS = "carbonblack_parents"
    CIPHERED_BUNDLED_FILES = "ciphered_bundled_files"
    CIPHERED_PARENTS = "ciphered_parents"
    COMPRESSED_PARENTS = "compressed_parents"
    EMAIL_ATTACHMENTS = "email_attachments"
    EMAIL_PARENTS = "email_parents"
    EMBEDDED_DOMAINS = "embedded_domains"
    EMBEDDED_IPS = "embedded_ips"
    EMBEDDED_URLS = "embedded_urls"
    ITW_DOMAINS = "itw_domains"
    ITW_IPS = "itw_ips"
    ITW_URLS = "itw_urls"
    MEMORY_PATTERN_DOMAINS = "memory_pattern_domains"
    MEMORY_PATTERN_IPS = "memory_pattern_ips"
    MEMORY_PATTERN_URLS = "memory_pattern_urls"
    OVERLAY_CHILDREN = "overlay_children"
    OVERLAY_PARENTS = "overlay_parents"
    PCAP_CHILDREN = "pcap_children"
    PCAP_PARENTS = "pcap_parents"
    SIMILAR_FILES = "similar_files"
    SUBMISSIONS = "submissions"
    SCREENSHOTS = "screenshots"
    URLS_FOR_EMBEDDED_JS = "urls_for_embedded_js"

    # Threat Landscape tier - VT Enterprise users with Threat Landscape
    RELATED_REFERENCES = "related_references"
    RELATED_THREAT_ACTORS = "related_threat_actors"
