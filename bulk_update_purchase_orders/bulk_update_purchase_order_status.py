"""
Given a list of purchase orders, update the status of the purchase order.
"""

import os
import sys
import inspect
from enum import Enum

# Reset the path so it can be run from the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import argparse
from getpass import getpass
from utilities.api import Api
import queries
from utilities.csv_helper import CsvHelper
from config import config
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="bulk_update_purchase_orders/log.txt",
    filemode="w",
)

valid_statuses = ["DRAFT", "REQUESTED", "APPROVED", "ORDERED", "CANCELED", "RECEIVED"]


def load_purchases() -> list[int]:
    """
    Load the purchase orders from the CSV file.
    """
    csv_data = CsvHelper.read_from_csv(
        "bulk_update_purchase_orders/update_purchase_orders.csv"
    )
    return [int(row[0]) for row in csv_data[1:]]


def get_purchase_order_etag(api: Api, purchase_order_id: int):
    """
    Get the etag of the purchase order.
    """
    request_body = {
        "query": queries.GET_PURCHASE_ORDER_ETAG,
        "variables": {"id": purchase_order_id},
    }
    purchase_order = api.request(request_body)["data"]
    return purchase_order["purchaseOrder"]["_etag"]


def bulk_update_purchase_order_status(
    api: Api, purchase_order_ids: list[int], status: str
):
    """
    Bulk update the status of the purchase orders.
    """
    for purchase_order_id in purchase_order_ids:
        logger.info(f"Updating purchase order {purchase_order_id} to {status} status")
        po_etag = get_purchase_order_etag(api, purchase_order_id)
        request_body = {
            "query": queries.UPDATE_PURCHASE,
            "variables": {
                "input": {"id": purchase_order_id, "etag": po_etag, "status": status}
            },
        }
        api.request(request_body)
        logger.info(f"Purchase order {purchase_order_id} updated to {status} status")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update purchase orders")
    parser.add_argument(
        "--status",
        required=True,
        type=str,
        choices=[status for status in valid_statuses],
        help=f"Status to set for the purchase orders. Valid values: {', '.join([status for status in valid_statuses])}",
    )
    args = parser.parse_args()

    try:
        auth_server = config["ION_AUTH_SERVER"]
        api_uri = config["ION_API_URI"]
        client_id = config["ION_CLIENT_ID"]
        client_secret = config["ION_CLIENT_SECRET"]
    except Exception as e:
        raise (f"Error with the config settings: {e}")

    try:
        api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
        )
    except Exception as e:
        raise (f"Error with the API settings: {e}")

    try:
        purchases = load_purchases()
        bulk_update_purchase_order_status(api, purchases, args.status)
        print(f"Purchase orders updated to {args.status} status")
    except Exception as e:
        raise (f"Error Updating Purchase Orders: {e}")
