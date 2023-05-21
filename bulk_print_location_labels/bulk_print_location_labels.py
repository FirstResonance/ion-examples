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

def get_templates(api):
    request_body = {
        "query": queries.GET_TEMPLATES,
        "variables": {
            "filters": {
                "entityType": {"eq": "LOCATIONS"}
            }
        }
    }
    return api.request(request_body)["data"]

def create_barcode_label(entity_id, template_id, api):
    request_body = {
        "query": queries.CREATE_BARCODE_LABEL,
        "variables": {
            'input': {
                'entityId': entity_id,
                'templateId': template_id
            }
        },
    }
    return api.request(request_body)["data"]

# Adapted from the below example
# https://www.zebra.com/us/en/support-downloads/knowledge-articles/ait/Network-Printing-Python-Example.html
def print_label(zpl_string, printer_ip):
    mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)         
    port = 9100
    try:           
        mysocket.connect((printer_ip, port)) #connecting to host
        mysocket.send(str.encode(zpl_string))#using bytes
        mysocket.close () #closing connection
    except:
        print("Error with the connection")

def get_csv_data():
    """Import csv data from file.

    Returns:
        Array of location data from csv.
    """
    csv_data = []
    with open('bulk_print_location_labels/locations.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for row in reader:
            csv_data.append(row)
    return csv_data

def get_location(location_id, api):
    location_input = {
        'id': location_id
    }
    request_body = {"query": queries.GET_LOCATION, "variables": location_input}
    return api.request(request_body)["data"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bulk print location barcode labels."
    )
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
        printer_ip = input('Enter the printer ip: ')
        for location in locations:
            location_data = get_location(location[0], ion_api)
            barcode_label = create_barcode_label(location_data['location']['entityId'], int(template_id), ion_api)
            print_label(barcode_label['createBarcodeLabel']['barcodeLabel']['barcode'], printer_ip)
    except Exception as e:
        error = f"Error occurred while running script: {e}"
        print(error)
        logger.exception(error)
