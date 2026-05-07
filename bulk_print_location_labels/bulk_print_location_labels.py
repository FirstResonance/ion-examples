"""
Bulk print location labels.
"""
import os
import sys
import inspect
import socket
import csv

# Reset the path so it can be run from the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from utilities.api import Api
import queries
from config import config

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="bulk_print_location_labels/log.txt",
    filemode="w",
)

# Zebra Browser Print listens on https://localhost:9101 with a self-signed cert.
BROWSER_PRINT_URL = "https://localhost:9101"

# Suppress the SSL warning for the self-signed localhost cert.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_templates(api):
    request_body = {
        "query": queries.GET_TEMPLATES,
        "variables": {"filters": {"entityType": {"eq": "LOCATIONS"}}},
    }
    return api.request(request_body)["data"]


def create_barcode_label(entity_id, template_id, api):
    request_body = {
        "query": queries.CREATE_BARCODE_LABEL,
        "variables": {"input": {"entityId": entity_id, "templateId": template_id}},
    }
    return api.request(request_body)["data"]


# Adapted from the below example
# https://www.zebra.com/us/en/support-downloads/knowledge-articles/ait/Network-Printing-Python-Example.html
def print_label_network(zpl_string, printer_ip):
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9100
    try:
        mysocket.connect((printer_ip, port))
        mysocket.send(str.encode(zpl_string))
        mysocket.close()
    except Exception as e:
        print(f"Error with the network connection: {e}")

def get_available_printers():
    """Return list of printer objects from the Zebra Browser Print agent."""
    try:
        response = requests.get(f"{BROWSER_PRINT_URL}/available", verify=False, timeout=3)
        response.raise_for_status()
        printers = response.json().get("printer", [])
        print(f"Found {len(printers)} printer(s): {[p.get('name') for p in printers]}")
        return printers
    except requests.exceptions.ConnectionError:
        print(
            "Could not connect to Zebra Browser Print at localhost:9101.\n"
            "Make sure Zebra Browser Print is installed and running:\n"
            "  https://www.zebra.com/us/en/support-downloads/printer-software/browser-print.html"
        )
        return []
    except Exception as e:
        print(f"Error querying Browser Print: {e}")
        return []

def print_label_usb(zpl_string, device):
    """POST raw ZPL to the Browser Print agent, which forwards it to the printer."""
    payload = {"device": device, "data": zpl_string}
    print(f"Device: {device.get('name')} ({device.get('connection')})")
    try:
        response = requests.post(
            f"{BROWSER_PRINT_URL}/write",
            json=payload,
            verify=False,
            timeout=10,
        )
        response.raise_for_status()
        print("Print job sent successfully.")
    except Exception as e:
        print(f"Error sending print job via Browser Print: {e}")

def select_usb_printer():
    """List available printers from Browser Print and prompt the user to pick one."""
    printers = get_available_printers()
    if not printers:
        return None
    if len(printers) == 1:
        print(f"Using printer: {printers[0].get('name', 'Unknown')}")
        return printers[0]
    print("Available printers:")
    for i, p in enumerate(printers):
        print(f"  [{i}] {p.get('name', 'Unknown')} ({p.get('connection', 'unknown')})")
    choice = input("Enter printer number: ").strip()
    try:
        return printers[int(choice)]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def get_csv_data():
    """Import csv data from file.

    Returns:
        Array of location data from csv.
    """
    csv_data = []
    with open("bulk_print_location_labels/locations.csv", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for row in reader:
            csv_data.append(row)
    return csv_data


def get_location(location_id, api):
    location_input = {"id": location_id}
    request_body = {"query": queries.GET_LOCATION, "variables": location_input}
    return api.request(request_body)["data"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk print location barcode labels.")
    try:
        auth_server = config["ION_AUTH_SERVER"]
        api_uri = config["ION_API_URI"]
        client_id = config["ION_CLIENT_ID"]
        client_secret = config["ION_CLIENT_SECRET"]
    except Exception as e:
        raise (f"Error with the config settings: {e}")
    try:
        ion_api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
            logger=logger,
        )
        locations = get_csv_data()
        templates = get_templates(ion_api)
        print(f'Available template: {templates}')
        template_id = input('Enter the template id: ')

        print("\nPrint via:")
        print("  [1] Network (IP address)")
        print("  [2] USB (via Zebra Browser Print)")
        connection_choice = input("Enter choice (1 or 2): ").strip()

        if connection_choice == '2':
            printer = select_usb_printer()
            if printer is None:
                sys.exit(1)
            for location in locations:
                location_data = get_location(location[0], ion_api)
                barcode_label = create_barcode_label(location_data['location']['entityId'], int(template_id), ion_api)
                print_label_usb(barcode_label['createBarcodeLabel']['barcodeLabel']['barcode'], printer)
        else:
            printer_ip = input('Enter the printer IP address: ')
            for location in locations:
                location_data = get_location(location[0], ion_api)
                barcode_label = create_barcode_label(location_data['location']['entityId'], int(template_id), ion_api)
                print_label_network(barcode_label['createBarcodeLabel']['barcodeLabel']['barcode'], printer_ip)
    except Exception as e:
        error = f"Error occurred while running script: {e}"
        print(error)
        logger.exception(error)
