"""
MCP Prompts for VT4AI - Analysis templates and workflows.
"""

from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all VT4AI prompts with the FastMCP server."""

    @mcp.prompt()
    def analyze_suspicious_file(file_hash: str, investigation_focus: str = "general") -> str:
        """Generate a prompt for comprehensive file analysis."""
        focus_areas = {
            "general": "overall threat assessment and key findings",
            "network": "network communications, C2 servers, and contacted domains",
            "behavior": "behavioral analysis, dropped files, and execution patterns",
            "attribution": "threat actor attribution, campaign tracking, and similar samples",
        }

        focus_desc = focus_areas.get(investigation_focus, focus_areas["general"])

        return f"""Please analyze the file with hash {file_hash} using the VT4AI tools. Focus on {focus_desc}.

Suggested analysis workflow:
1. Get the basic file report: get_file_report(file_hash="{file_hash}")
2. Check network relationships: get_file_relationships(file_hash="{file_hash}", relationship="contacted_domains")
3. Look for behavioral indicators: get_file_relationships(file_hash="{file_hash}", relationship="behaviours")
4. Find similar samples: get_file_relationships(file_hash="{file_hash}", relationship="similar_files")

Provide a comprehensive analysis including threat level, key indicators, and recommended actions."""

    @mcp.prompt()
    def investigate_domain(domain: str, check_related: bool = True) -> str:
        """Generate a prompt for domain investigation."""
        prompt = f"""Please investigate the domain {domain} for security threats and reputation issues.

Analysis steps:
1. Get domain report: get_domain_report(domain="{domain}")
2. Analyze the results for:
   - Malicious detections
   - DNS records and infrastructure
   - SSL certificate information
   - Historical analysis data
   - Community reputation scores
"""

        if check_related:
            prompt += """
3. If the domain appears suspicious, also check:
   - Any associated IP addresses found in the domain report
   - Related domains through WHOIS or certificate data
"""

        prompt += "\nProvide a risk assessment and recommendations based on the findings."
        return prompt

    @mcp.prompt()
    def analyze_url_threat(url: str, include_relationships: bool = False) -> str:
        """Generate a prompt for URL threat analysis."""
        prompt = f"""Please analyze the URL {url} for potential security threats.

Analysis workflow:
1. Get URL report: get_url_report(url="{url}")
2. Review the analysis for:
   - Malicious classifications from security vendors
   - Redirections and final destinations
   - Associated domains and IP addresses
   - Historical scan results
   - Community feedback and reputation
"""

        if include_relationships:
            prompt += """
3. If the URL appears suspicious, investigate related entities:
   - Domain reputation of the host
   - IP address analysis
   - Similar URLs or patterns
"""

        prompt += """

Provide a threat assessment including:
- Risk level (Low/Medium/High)
- Specific threats identified
- Recommended actions for users/administrators
- Any indicators of compromise (IoCs)
"""
        return prompt

    @mcp.prompt()
    def investigate_ip_address(ip: str, deep_analysis: bool = True) -> str:
        """Generate a prompt for IP address investigation."""
        prompt = f"""Please investigate the IP address {ip} for security threats and reputation.

Basic analysis:
1. Get IP report: get_ip_report(ip="{ip}")
2. Review findings for:
   - Malicious activity detections
   - Geolocation and ASN information
   - Associated domains and URLs
   - Network infrastructure details
   - Historical reputation data
"""

        if deep_analysis:
            prompt += """
Advanced analysis:
3. If suspicious activity is found, investigate:
   - Associated domains hosted on this IP
   - Related IP ranges or subnets
   - Patterns of malicious behavior
   - Attribution to known threat actors
"""

        prompt += """

Provide a comprehensive assessment including:
- Security risk level
- Types of threats associated with this IP
- Recommended defensive measures
- Any relevant threat intelligence context
"""
        return prompt
