# Download Supplier Attribute Files

A Python script to download files from supplier attributes via the ION GraphQL API.

## Description

This script authenticates with the ION API, queries supplier attributes containing file URLs, and downloads those files to a local directory. It supports downloading files for a specific supplier or all suppliers at once.

## Prerequisites

- Python 3.x
- Required packages:
  ```bash
  pip install requests
  ```

## Authentication

The script uses OAuth2 client credentials to authenticate with the ION API. You'll need:
- **Client ID** - Your ION API client ID
- **Client Secret** - Your ION API client secret
- **Auth Server** - The ION authentication server (e.g., `auth.buildwithion.com`)

## Usage

```bash
python download-supplier-attribute-files.py \
  --client-id <CLIENT_ID> \
  --client-secret <CLIENT_SECRET> \
  --auth-server <AUTH_SERVER> \
  --endpoint <GRAPHQL_ENDPOINT> \
  --attribute-names <ATTRIBUTE_NAMES> \
  [--supplier-name <SUPPLIER_NAME>] \
  [--output-dir <OUTPUT_DIR>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--client-id` | Yes | ION API Client ID |
| `--client-secret` | Yes | ION API Client Secret |
| `--auth-server` | Yes | ION Auth Server (e.g., `auth.buildwithion.com`) |
| `--endpoint` | Yes | GraphQL API endpoint URL |
| `--attribute-names` | Yes | Comma-separated list of attribute names to download |
| `--supplier-name` | No | Supplier name to filter by (omit to download for all suppliers) |
| `--output-dir` | No | Output directory for downloaded files (default: current directory) |

## Examples

### Download files for a specific supplier

```bash
python download-supplier-attribute-files.py \
  --client-id my-client-id \
  --client-secret my-client-secret \
  --auth-server auth.buildwithion.com \
  --endpoint https://api.example.com/ \
  --supplier-name "Acme Corp" \
  --attribute-names "Brochure, Sales Collateral" \
  --output-dir ./downloads
```

### Download files for all suppliers

```bash
python download-supplier-attribute-files.py \
  --client-id my-client-id \
  --client-secret my-client-secret \
  --auth-server auth.buildwithion.com \
  --endpoint https://api.example.com/ \
  --attribute-names "Brochure, Sales Collateral" \
  --output-dir ./downloads
```

### Download a single attribute type

```bash
python download-supplier-attribute-files.py \
  --client-id my-client-id \
  --client-secret my-client-secret \
  --auth-server auth.buildwithion.com \
  --endpoint https://api.example.com/ \
  --attribute-names "Brochure"
```

## Output

Downloaded files are named using the format:
```
{supplier_name}-{attribute_key}.{extension}
```

For example:
- `Acme_Corp-Brochure.pdf`
- `Acme_Corp-Sales_Collateral.pdf`

## Logging

The script logs all operations to both:
- Console (stdout)
- `download-supplier-attribute-files.log` file

Log entries include timestamps, log levels, and detailed information about each operation.

