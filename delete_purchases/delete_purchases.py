"""
Delete purchases.
Deletes all PO lines (ones associated with aboms, kits, or that have been received) can't be deleted. 
Deletes all purchase orders that don't have receipts or PO lines, approvals, fees, or approval requests.
You can additionally add PO ids that you don't want deleted in PURCHASES_TO_SKIP
"""
import os
import sys
import inspect

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
    filename="delete_purchases/log.txt",
    filemode="w",
)

PURCHASES_TO_SKIP=[]

def get_receipts(api):
    request_body = {"query": queries.GET_RECEIPTS}
    return api.request(request_body)["data"]

def get_purchase_lines(api):
    request_body = {"query": queries.GET_PURCHASE_LINES}
    return api.request(request_body)["data"]

def get_purchase_line_etag(id,api):
    request_body = {"query": queries.GET_PURCHASE_LINE_ETAG, "variables": {"id": id}}
    purchase_line = api.request(request_body)["data"]
    _etag = purchase_line["purchaseOrderLine"]["_etag"]
    return _etag

def get_purchases(api):
    request_body = {"query": queries.GET_PURCHASES}
    return api.request(request_body)["data"]

def update_ordered_status_to_draft(po_id,po_etag,api):
    request_body = {
                "query": queries.UPDATE_PURCHASE,
                "variables": { "input": {
                "id": po_id,
                "etag": po_etag,
                "status": "DRAFT"
                        }
                    }
                }   
    api.request(request_body)

def build_list_aboms_items(purchase_order_lines):
    for purchase_order_line in purchase_order_lines["purchaseOrderLines"]["edges"]:
        if "partInventories" in purchase_order_line["node"]:
            if (any(part_inventory["installed"] for part_inventory in purchase_order_line["node"]["partInventories"]) or 
                any(part_inventory["kitted"] for part_inventory in purchase_order_line["node"]["partInventories"]) or 
                any(part_inventory["received"] for part_inventory in purchase_order_line["node"]["partInventories"]) or 
                any(abom_child.get("partInventoryId") is not None for part_inventory in purchase_order_line["node"]["partInventories"] for abom_child in part_inventory.get("abomChildren", []))):
                po_id = purchase_order_line["node"]["purchaseOrder"]["id"]
                if po_id not in PURCHASES_TO_SKIP:
                    PURCHASES_TO_SKIP.append(po_id)

def delete_purchase_lines(purchase_lines, api):
    for purchase_line in purchase_lines["purchaseOrderLines"]["edges"]:
        po_id = purchase_line["node"]["purchaseOrder"]["id"]
        po_etag = purchase_line["node"]["purchaseOrder"]["_etag"]
        po_status = purchase_line["node"]["purchaseOrder"]["status"]
        purchase_line_id = purchase_line["node"]["id"]
        etag = get_purchase_line_etag(purchase_line_id,api)
        if (po_id in PURCHASES_TO_SKIP):
            logger.info(f'Skipping PO line: {purchase_line_id}')
            continue
        if (po_status == "ORDERED"):
            update_ordered_status_to_draft(po_id,po_etag,api)
        logger.info(f'Deleting purchase line id: {purchase_line_id}')
        etag = get_purchase_line_etag(purchase_line_id,api)
        request_body = {
            "query": queries.DELETE_PURCHASE_LINE,
            "variables": {"id": purchase_line_id, "etag": etag},
        }
        api.request(request_body)

def delete_purchases(purchases, api):
    for purchase in purchases["purchaseOrders"]["edges"]:
        purchase_id = purchase["node"]["id"]
        etag = purchase["node"]["_etag"]
        if purchase_id in PURCHASES_TO_SKIP or purchase["node"]["approvals"] or purchase["node"]["fees"] or purchase["node"]["approvalRequests"]:
            logger.info(f'skipping purchase id: {purchase_id}')
            continue
        logger.info(f'deleting purchase id: {purchase_id}')
        request_body = {
            "query": queries.DELETE_PURCHASE,
            "variables": {"id": purchase_id, "etag": etag},
        }
        api.request(request_body)

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

        receipts = get_receipts(ion_api)
        purchase_lines = get_purchase_lines(ion_api)
        purchases = get_purchases(ion_api)
        build_list_aboms_items(purchase_lines)
        delete_purchase_lines(purchase_lines, ion_api)
        delete_purchases(purchases,ion_api)
    except KeyError as e:
        print(f"KeyError occurred: {e}")
    except Exception as e:
        error = f"Error occurred while running script: {e}"
        print(error)
        logger.exception(error)
