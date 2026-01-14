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

## Configuration

1. Copy `config_example.py` to `config.py`:
   ```bash
   cp config_example.py config.py
   ```

2. Edit `config.py` with your ION API credentials:
   ```python
   config = {
       "ION_AUTH_SERVER": "auth.buildwithion.com",
       "ION_API_URI": "https://api.buildwithion.com",
       "ION_CLIENT_ID": "your-client-id",
       "ION_CLIENT_SECRET": "your-client-secret",
   }
   ```

## Usage

Run from the `download_supplier_attribute_files` directory:

```bash
python download-supplier-attribute-files.py \
  --attribute-names <ATTRIBUTE_NAMES> \
  [--supplier-name <SUPPLIER_NAME>] \
  [--output-dir <OUTPUT_DIR>] \
  [--force] \
  [--timeout <SECONDS>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--attribute-names` | Yes | Comma-separated list of attribute names to download |
| `--supplier-name` | No | Supplier name to filter by (omit to download for all suppliers) |
| `--output-dir` | No | Output directory for downloaded files (default: current directory) |
| `--force` | No | Overwrite existing files without warning |
| `--timeout` | No | Download timeout in seconds (default: 60) |

## Examples

### Download files for a specific supplier

```bash
python download-supplier-attribute-files.py \
  --supplier-name "Acme Corp" \
  --attribute-names "Brochure, Sales Collateral" \
  --output-dir ./downloads
```

### Download files for all suppliers

```bash
python download-supplier-attribute-files.py \
  --attribute-names "Brochure, Sales Collateral" \
  --output-dir ./downloads
```

### Download a single attribute type

```bash
python download-supplier-attribute-files.py \
  --attribute-names "Brochure"
```

### Force overwrite existing files

```bash
python download-supplier-attribute-files.py \
  --attribute-names "Brochure" \
  --output-dir ./downloads \
  --force
```

### Set a custom timeout for slow connections

```bash
python download-supplier-attribute-files.py \
  --attribute-names "Brochure" \
  --timeout 120
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
- `download-supplier-attribute-files.log` file in the script directory

Log entries include timestamps, log levels, and detailed information about each operation.

## Features

- **Pagination support**: Automatically handles large numbers of suppliers by fetching results in pages
- **URL validation**: Validates attribute URLs before attempting to download
- **Timeout protection**: Configurable timeout prevents hanging on slow or unresponsive servers
- **Safe file naming**: Sanitizes supplier names and attribute keys for safe filesystem usage
- **Overwrite protection**: By default, skips existing files (use `--force` to overwrite)
