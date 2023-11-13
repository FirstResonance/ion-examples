"""
Delete purchases.
Deletes all Receipts (ones associated with PO Lines can't be deleted)
Deletes all PO lines (ones associated with POs can't be deleted)
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

def build_list_aboms_items(purchase_order_lines):
    list_of_pos = set()
    for purchase_order_line in purchase_order_lines["purchaseOrderLines"]["edges"]:
        if "partInventories" in purchase_order_line["node"]:
            if any(part_inventory["installed"] for part_inventory in purchase_order_line["node"]["partInventories"]) or any(part_inventory["kitted"] for part_inventory in purchase_order_line["node"]["partInventories"])or any(part_inventory["received"] for part_inventory in purchase_order_line["node"]["partInventories"]):
                po_id = purchase_order_line["node"]["purchaseOrder"]["id"]
                list_of_pos.add(po_id)
    return list(list_of_pos)

def build_list_receipts(receipts):
    LIST_OF_POS = []
    for receipt in receipts["receipts"]["edges"]:
        polines = receipt["node"]["purchaseOrderLines"]
        for poline in polines:
            poline_id = poline["id"]
            LIST_OF_POS.append(poline_id)
    return LIST_OF_POS

def delete_receipts(receipts, api):
    for receipt in receipts["receipts"]["edges"]:
        receipt_id = receipt["node"]["id"]
        print('Deleting receipt id: ',receipt_id)
        etag = receipt["node"]["_etag"]
        request_body = {
            "query": queries.DELETE_RECEIPT,
            "variables": {"id": receipt_id, "etag": etag},
        }
        api.request(request_body)

def delete_purchase_lines(purchase_lines, api):
    LIST_POS = set()
    POS_WITH_ABOMITEMS_TO_SKIP = build_list_aboms_items(purchase_lines)
    for purchase_line in purchase_lines["purchaseOrderLines"]["edges"]:
        po_id = purchase_line["node"]["purchaseOrder"]["id"]
        po_status =  purchase_line["node"]["purchaseOrder"]["status"]
        purchase_line_id = purchase_line["node"]["id"]
        etag=get_purchase_line_etag(purchase_line_id,api)
        if po_id in POS_WITH_ABOMITEMS_TO_SKIP or po_status == 'CANCELED' or po_status == 'RECEIVED':
            print("Skipping PO LINE",purchase_line_id)
            LIST_POS.add(po_id)
            continue
        print("Deleting purchase line id",purchase_line_id)
        request_body = {
            "query": queries.DELETE_PURCHASE_LINE,
            "variables": {"id": purchase_line_id, "etag": etag},
        }
        api.request(request_body)
    return list(LIST_POS)

def delete_purchases(pos_to_save,purchases, api):
    POS_WITH_RECEIPTS_TO_SKIP = build_list_receipts(receipts)
    for purchase in purchases["purchaseOrders"]["edges"]:
        purchase_id = purchase["node"]["id"]
        etag = purchase["node"]["_etag"]
        if purchase_id in PURCHASES_TO_SKIP or purchase_id in POS_WITH_RECEIPTS_TO_SKIP or purchase_id in pos_to_save:
            print("skipping purchase id",purchase_id)
            continue
        if purchase["node"]["approvals"] or purchase["node"]["fees"] or purchase["node"]["approvalRequests"]:
            print("skipping purchase id", purchase_id)
            continue
        print("deleting purchase id",purchase_id)
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
           #logger=logger,
        )
        receipts = get_receipts(ion_api)
        purchase_lines = get_purchase_lines(ion_api)
        pos_to_save = delete_purchase_lines(purchase_lines, ion_api)
        purchases = get_purchases(ion_api)
        delete_purchases(pos_to_save,purchases,ion_api)
    except KeyError as e:
        print(f"KeyError occurred: {e}")
    except Exception as e:
        print(f"General error occurred: {e}")
