"""
Download supplier attribute files.
Downloads files from supplier attributes by attribute name(s).
Optionally filter by supplier name, otherwise downloads for all suppliers.
"""
import argparse
import logging
import os
import re
import sys
from typing import Optional
from urllib.parse import urlparse, unquote

import requests

# Add parent directory to path for local imports
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from config import config
from utilities.api import Api

# Configure logging with absolute path for log file
log_file = os.path.join(currentdir, "download-supplier-attribute-files.log")
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Constants
DEFAULT_TIMEOUT = 60  # seconds
PAGE_SIZE = 100  # Number of suppliers per page


def format_attribute_names(attribute_names_csv: str) -> list[str]:
    """Convert comma-separated attribute names to list format.
    
    Args:
        attribute_names_csv: Comma-separated string of attribute names
        
    Returns:
        List of trimmed attribute names
    
    Example:
        Input: "Brochure, Sales Collateral"
        Output: ["Brochure", "Sales Collateral"]
    """
    return [name.strip() for name in attribute_names_csv.split(',')]


def get_attribute_files(
    api: Api,
    supplier_name: Optional[str] = None,
    page_size: int = PAGE_SIZE
) -> list[dict]:
    """Get supplier attributes from the API with pagination support.
    
    Args:
        api: Api instance for making requests
        supplier_name: Optional supplier name to filter by
        page_size: Number of results per page
        
    Returns:
        List of supplier edges or empty list if no suppliers found
    """
    # Build filters
    supplier_filters = {}
    if supplier_name:
        supplier_filters["name"] = {"eq": supplier_name}
    
    query = """
    query GetSupplierAttributes($supplierFilters: SuppliersInputFilters, $first: Int, $after: String) {
      suppliers(filters: $supplierFilters, first: $first, after: $after) {
        edges {
          node {
            id
            name
            Attributes {
              key
              value
              type
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    
    all_edges = []
    has_next_page = True
    cursor = None
    page_num = 1
    
    while has_next_page:
        variables = {
            "first": page_size,
        }
        if supplier_filters:
            variables["supplierFilters"] = supplier_filters
        if cursor:
            variables["after"] = cursor
        
        request_body = {
            "query": query,
            "variables": variables
        }
        
        logger.info(f"Querying suppliers (page {page_num})...")
        result = api.request(request_body)
        
        if not result or "data" not in result:
            logger.warning("No data returned from API")
            break
            
        suppliers_data = result["data"].get("suppliers")
        if not suppliers_data:
            logger.warning("No suppliers data in response")
            break
            
        edges = suppliers_data.get("edges", [])
        if edges:
            all_edges.extend(edges)
            logger.info(f"Retrieved {len(edges)} suppliers on page {page_num}")
        
        page_info = suppliers_data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")
        page_num += 1
    
    logger.info(f"Total suppliers retrieved: {len(all_edges)}")
    return all_edges


def is_valid_url(url: str) -> bool:
    """Validate that a string is a properly formatted URL.
    
    Args:
        url: String to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def download_file(url: str, filename: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Download a file from a URL.
    
    Args:
        url: URL to download from
        filename: Local filename to save to
        timeout: Request timeout in seconds
        
    Raises:
        requests.exceptions.RequestException: If download fails
    """
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()
    
    # Log file size if available
    content_length = response.headers.get('content-length')
    if content_length:
        size_mb = int(content_length) / 1024 / 1024
        logger.info(f"Downloading {size_mb:.2f} MB...")
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def process_suppliers(
    nodes: list[dict],
    output_dir: str,
    attribute_names_csv: str,
    force_overwrite: bool = False
) -> None:
    """Process supplier nodes and download their attribute files.
    
    Args:
        nodes: List of supplier edges from the API
        output_dir: Directory to save downloaded files
        attribute_names_csv: Comma-separated string of attribute names to filter by
        force_overwrite: If True, overwrite existing files without warning
    """
    filter_names = format_attribute_names(attribute_names_csv)
    
    for edge in nodes:
        supplier = edge['node']
        supplier_name = supplier['name']
        logger.info(f"Processing supplier: {supplier_name}")
        
        all_attributes = supplier.get('Attributes', [])
        
        # Filter attributes by the specified names and ensure they are FILE_ATTACHMENT type
        attributes = []
        for attr in all_attributes:
            if attr['key'] in filter_names:
                if attr.get('type') == 'FILE_ATTACHMENT':
                    attributes.append(attr)
                else:
                    logger.warning(
                        f"Supplier '{supplier_name}' attribute '{attr['key']}' is type "
                        f"'{attr.get('type')}', expected 'FILE_ATTACHMENT'. Skipping."
                    )
        
        if not attributes:
            logger.debug(f"No matching FILE_ATTACHMENT attributes found for '{supplier_name}'")
            continue

        for attr in attributes:
            key = attr['key']
            url = attr['value']
            
            if not url:
                logger.warning(f"Supplier '{supplier_name}' has empty URL for attribute '{key}', skipping.")
                continue
            
            if not is_valid_url(url):
                logger.warning(f"Supplier '{supplier_name}' has invalid URL for attribute '{key}': {url}")
                continue
            
            try:
                # Extract file extension from URL path (before query params)
                parsed_url = urlparse(url)
                url_path = unquote(parsed_url.path)
                _, ext = os.path.splitext(url_path)
                
                # Sanitize supplier name and key for use in filename
                safe_supplier_name = re.sub(r'[^\w\s-]', '', supplier_name).strip().replace(' ', '_')
                safe_key = re.sub(r'[^\w\s-]', '', key).strip().replace(' ', '_')
                
                # Create filename: supplier_name-attribute_key.extension
                filename = os.path.join(output_dir, f"{safe_supplier_name}-{safe_key}{ext}")
                
                # Check if file exists and handle accordingly
                if os.path.exists(filename) and not force_overwrite:
                    logger.warning(f"File '{filename}' already exists, skipping. Use --force to overwrite.")
                    continue
                
                logger.info(f"Downloading '{key}' for supplier '{supplier_name}' to '{filename}'...")
                download_file(url, filename)
                logger.info(f"Successfully downloaded '{filename}'")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download file for supplier '{supplier_name}', attribute '{key}': {e}")
            except Exception as e:
                logger.error(f"Error processing attribute '{key}' for supplier '{supplier_name}': {e}")


def validate_config(config_dict: dict) -> tuple[str, str, str, str]:
    """Validate and extract required configuration values.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Tuple of (auth_server, api_uri, client_id, client_secret)
        
    Raises:
        ValueError: If required configuration keys are missing
    """
    required_keys = ["ION_AUTH_SERVER", "ION_API_URI", "ION_CLIENT_ID", "ION_CLIENT_SECRET"]
    missing_keys = [key for key in required_keys if key not in config_dict]
    
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")
    
    return (
        config_dict["ION_AUTH_SERVER"],
        config_dict["ION_API_URI"],
        config_dict["ION_CLIENT_ID"],
        config_dict["ION_CLIENT_SECRET"]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download supplier attribute files.")
    parser.add_argument('--supplier-name', help='Supplier name (omit to download for all suppliers)')
    parser.add_argument('--attribute-names', required=True, help='Comma separated list of attribute names')
    parser.add_argument('--output-dir', default='.', help='Output directory for downloaded files (default: current directory)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files without warning')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help=f'Download timeout in seconds (default: {DEFAULT_TIMEOUT})')
    args = parser.parse_args()
    
    try:
        auth_server, api_uri, client_id, client_secret = validate_config(config)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    try:
        ion_api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
            logger=logger,
        )
        
        if args.supplier_name:
            logger.info(f"Downloading files for supplier: {args.supplier_name}")
        else:
            logger.info("Downloading files for all suppliers")
        
        nodes = get_attribute_files(ion_api, args.supplier_name)
        
        if not nodes:
            logger.info("No suppliers found.")
        else:
            # Create output directory if it doesn't exist
            output_dir = args.output_dir
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            
            process_suppliers(nodes, output_dir, args.attribute_names, args.force)
            
    except Exception as e:
        error = f"Error occurred while running script: {e}"
        logger.exception(error)
        sys.exit(1)
