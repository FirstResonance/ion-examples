"""
Update inventory quantities from a csv. 
"""
import os
import sys
import inspect
import re
import decimal


# Reset the path so it can be run from the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import argparse
from utilities.api import Api
from utilities.csv_helper import CsvHelper
import queries
from config import config
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="inventory_updates/log.txt",
    filemode="w",
)


def get_inventory(api: Api, part_inventory_id: int):
    """Get inventory info for given id."""
    request_body = {
        "query": queries.GET_PART_INVENTORY,
        "variables": {"id": part_inventory_id},
    }
    res = api.request(request_body)
    logger.info(f"Response: {res}")
    return res["data"]["partInventory"]


def update_inventory(api: Api, inventory: dict, new_quantity: float):
    """Update inventory with new quantity."""
    request_body = {
        "query": queries.UPDATE_PART_INVENTORY,
        "variables": {
            "input": {
                "id": inventory["id"],
                "etag": inventory["_etag"],
                "quantity": new_quantity,
            }
        },
    }
    res = api.request(request_body)
    logger.info(f"Response: {res}")
    return res["data"]["updatePartInventory"]["partInventory"]


def update_inventory_quantities(api, csv_data):
    items_length = len(csv_data) - 1
    logger.info(f"{items_length} inventories to process.")
    for index, row in enumerate(csv_data):
        if index == 0:
            continue
        logger.info(f"Processing row {index}/{items_length}")
        inventory = get_inventory(api, row[0])
        # Remove excess 0s at end of decimal
        new_quantity = str(decimal.Decimal(row[1]).normalize())
        updated_inventory = update_inventory(api, inventory, new_quantity)
        logger.info("Inventory updated. Response: {updated_inventory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Round inventory quantity to specified decimal precision."
    )
    try:
        auth_server = config["ION_AUTH_SERVER"]
        api_uri = config["ION_API_URI"]
        client_id = config["ION_CLIENT_ID"]
        client_secret = config["ION_CLIENT_SECRET"]
    except Exception as e:
        print(f"Error with the config settings: {e}")
        raise (e)

    try:
        api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
        )
        csv_data = CsvHelper.read_from_csv("inventory_updates/inventory_update.csv")
        update_inventory_quantities(api, csv_data)
        print("Completed inventory updates.")
    except Exception as e:
        print(f"Error occurred while running script: {e}")
        raise (e)
