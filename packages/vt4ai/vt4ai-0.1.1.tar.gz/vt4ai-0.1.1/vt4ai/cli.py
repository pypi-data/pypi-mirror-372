import argparse
import asyncio
import hashlib
import os
import sys
from typing import Optional

from vt4ai.client import VT4AIClient
from vt4ai.constants.file_relationships import FileRelationship
from vt4ai.constants.output_formats import AvailableFormats


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Calculate hash of a file using the specified algorithm."""
    hash_func = getattr(hashlib, algorithm.lower())()

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find file: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")


async def main():
    parser = argparse.ArgumentParser(
        description="VT4AI CLI - A tool to query VirusTotal for AI-optimized reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Get a file report by hash in JSON format
  %(prog)s --hash 1234567890abcdef

  # Get a domain report in Markdown using a specific template
  %(prog)s --domain virustotal.com --format markdown --template-name vt4ai_domain_basics

  # Get an IP report in XML
  %(prog)s --ip 8.8.8.8 --format xml

  # Get a URL report
  %(prog)s --url "http://example.com"

  # Get a file report by calculating its hash, using a specific algorithm
  %(prog)s --file /path/to/file --algorithm md5

  # Get contacted domains for a file
  %(prog)s --file /path/to/file --relationship contacted_domains --limit 5

Required environment variables:
  VT4AI_API_KEY    Your VirusTotal API key
        """,
    )

    # --- Target Arguments (mutually exclusive) ---
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--hash",
        "-H",
        type=str,
        help="File hash to query (MD5, SHA1 or SHA256)",
    )
    target_group.add_argument(
        "--file", "-f", type=str, help="File path to calculate hash and query"
    )
    target_group.add_argument("--domain", "-d", type=str, help="Domain name to query")
    target_group.add_argument("--ip", "-i", type=str, help="IP address to query")
    target_group.add_argument("--url", "-u", type=str, help="URL to query")

    # --- Options for File Targets ---
    file_options = parser.add_argument_group("File-specific options")
    file_options.add_argument(
        "--algorithm",
        "-a",
        type=str,
        choices=["md5", "sha1", "sha256"],
        default="sha256",
        help="Hash algorithm for file analysis (default: sha256)",
    )
    file_options.add_argument(
        "--relationship",
        "-r",
        type=str,
        choices=[rel.value for rel in FileRelationship],
        help="Get objects related to a file",
    )
    file_options.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="Limit results for relationship queries (default: 10)",
    )
    file_options.add_argument(
        "--cursor",
        "-c",
        type=str,
        help="Pagination cursor for relationship queries",
    )

    # --- General Options ---
    general_options = parser.add_argument_group("General options")
    general_options.add_argument(
        "--format",
        "-fmt",
        type=str,
        choices=[fmt.value for fmt in AvailableFormats],
        default=AvailableFormats.JSON.value,
        help="Output format for the report (default: json)",
    )
    general_options.add_argument(
        "--template-name",
        "-t",
        type=str,
        help="Name of a specific template to apply for filtering",
    )
    general_options.add_argument(
        "--api-key",
        "-k",
        type=str,
        help="VirusTotal API key (overrides VT4AI_API_KEY env var)",
    )
    general_options.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # --- API Key Resolution ---
    api_key = args.api_key or os.getenv("VT4AI_API_KEY")
    if not api_key:
        print("Error: A VirusTotal API key is required.", file=sys.stderr)
        print(
            "Provide it via --api-key or the VT4AI_API_KEY environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Argument Validation and Logic ---
    if args.relationship and not (args.file or args.hash):
        print(
            "Error: --relationship can only be used with --file or --hash.",
            file=sys.stderr,
        )
        sys.exit(1)

    query_target = None
    query_type = None
    file_hash_target = None

    if args.file:
        try:
            if args.verbose:
                print(f"Calculating {args.algorithm.upper()} hash for: {args.file}")
            file_hash_target = calculate_file_hash(args.file, args.algorithm)
            if args.verbose:
                print(f"Calculated hash: {file_hash_target}")
            query_type = "relationship" if args.relationship else "file"
        except Exception as e:
            print(f"Error processing file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.hash:
        file_hash_target = args.hash
        query_type = "relationship" if args.relationship else "file"
    elif args.domain:
        query_type = "domain"
        query_target = args.domain
    elif args.ip:
        query_type = "ip"
        query_target = args.ip
    elif args.url:
        query_type = "url"
        query_target = args.url

    # --- Execute Query ---
    try:
        async with VT4AIClient(api_key) as client:
            report = None
            output_format = AvailableFormats(args.format)
            template: Optional[str] = args.template_name

            if args.verbose:
                print(f"Querying VirusTotal for {query_type}: {query_target or file_hash_target}")
                if template:
                    print(f"Using template: {template}")
                print(f"Requesting format: {output_format.value}")

            if query_type == "file":
                report = await client.get_file_report_by_hash(
                    file_hash_target, output_format, template
                )
            elif query_type == "domain":
                report = await client.get_domain_report(query_target, output_format, template)
            elif query_type == "ip":
                report = await client.get_ip_report(query_target, output_format, template)
            elif query_type == "url":
                report = await client.get_url_report(query_target, output_format, template)
            elif query_type == "relationship":
                report = await client.get_file_report_with_relationships_descriptors(
                    file_hash=file_hash_target,
                    relationship=args.relationship,
                    format_enum=output_format,
                    template_name=template,
                    limit=args.limit,
                    cursor=args.cursor,
                )

            if report:
                print(report)

    except Exception as e:
        print(f"An error occurred during the API call: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
