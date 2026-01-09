import requests
import logging
import argparse
import os
import re
from urllib.parse import urljoin, urlparse, unquote


# LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("download-supplier-attribute-files.log"),
        logging.StreamHandler()
    ]
)


# AUTHENTICATION
def get_access_token(auth_server, client_id, client_secret):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    logging.info("Requesting ION token...")
    auth_url = 'https://' + auth_server + '/realms/api-keys/protocol/openid-connect/token'
    response = requests.post(auth_url, headers=headers, data=data)
    response.raise_for_status()
    token = response.json()['access_token']
    logging.info("Token retrieved successfully.")
    return f"Bearer {token}"


# GRAPHQL HELPERS
def run_graphql_query(endpoint: str, headers: dict, query: str, variables: str):
    try:
        response = requests.post(urljoin(endpoint, 'graphql'), headers=headers, json={
            'query': query,
            'variables': variables
        })
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error running query: {query}\nwith variables: {variables}\nexception: {e}")
        return None


def format_attribute_keys(attribute_names):
    """Convert comma-separated attribute names to GraphQL list format.
    
    Input: "Brochure, Sales Collateral"
    Output: "Brochure","Sales Collateral"
    """
    keys = [key.strip() for key in attribute_names.split(',')]
    return ','.join(f'"{key}"' for key in keys)


def get_attribute_files(endpoint, headers, supplier_name, attribute_keys):
    formatted_keys = format_attribute_keys(attribute_keys)
    supplier_filter = f'(filters: {{name: {{eq: "{supplier_name}"}}}})' if supplier_name else ''
    query = f'''
    {{
      suppliers{supplier_filter} {{
        edges {{
          node {{
            id
            name
            Attributes(filters: {{key: {{in: [{formatted_keys}]}}}}) {{
              key
              value
            }}
          }}
        }}
      }}
    }}
    '''
    logging.info(query)
    result = run_graphql_query(endpoint, headers, query, '')
    if result is not None:
        edges = result['data']['suppliers']['edges']
        return edges if edges else None
    else:
        return None


def main(args):
    token = get_access_token(args.auth_server, args.client_id, args.client_secret)
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    if args.supplier_name:
        logging.info(f"Downloading files for supplier: {args.supplier_name}")
    else:
        logging.info("Downloading files for all suppliers")

    nodes = get_attribute_files(args.endpoint, headers, args.supplier_name, args.attribute_names)

    if not nodes:
        logging.info("No suppliers found.")
        return

    # Create output directory if it doesn't exist
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    for edge in nodes:
        supplier = edge['node']
        supplier_name = supplier['name']
        attributes = supplier.get('Attributes', [])
        logging.info(f"Downloading files for supplier: {supplier_name} to directory: {output_dir}")

        try:
            for attr in attributes:
                key = attr['key']
                url = attr['value']
                
                if not url:
                    logging.warning(f"Supplier '{supplier_name}' has empty URL for attribute '{key}', skipping.")
                    continue
                
                # Extract file extension from URL path (before query params)
                parsed_url = urlparse(url)
                url_path = unquote(parsed_url.path)
                _, ext = os.path.splitext(url_path)
                
                # Sanitize supplier name and key for use in filename
                safe_supplier_name = re.sub(r'[^\w\s-]', '', supplier_name).strip().replace(' ', '_')
                safe_key = re.sub(r'[^\w\s-]', '', key).strip().replace(' ', '_')
                
                # Create filename: supplier_name-attribute_key.extension
                filename = os.path.join(output_dir, f"{safe_supplier_name}-{safe_key}{ext}")
                
                logging.info(f"Downloading '{key}' for supplier '{supplier_name}' to '{filename}'...")
                
                # Download the file
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logging.info(f"Successfully downloaded '{filename}'")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download file for supplier '{supplier_name}': {e}")
        except Exception as e:
            logging.error(f"Error processing supplier '{supplier_name}': {e}")


# ENTRY POINT
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download supplier attribute files.')
    parser.add_argument('--client-id', required=True, help='ION Client ID')
    parser.add_argument('--client-secret', required=True, help='ION Client Secret')
    parser.add_argument('--auth-server', required=True, help='ION Auth Server (e.g. auth.buildwithion.com)')
    parser.add_argument('--endpoint', required=True, help='GraphQL API endpoint URL')
    parser.add_argument('--supplier-name', help='Supplier name (omit to download for all suppliers)')
    parser.add_argument('--attribute-names', required=True, help='Comma separated list of attribute names')
    parser.add_argument('--output-dir', default='.', help='Output directory for downloaded files (default: current directory)')
    args = parser.parse_args()
    main(args)
