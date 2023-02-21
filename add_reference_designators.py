"""
Given list of reference designators, add to mBOM ID. 
"""

import argparse
from getpass import getpass
from utilities.api import Api
import queries
from utilities.csv_helper import CsvHelper


def add_reference_designator(api: Api, mbom_item_id: int, value: str):
    """
    Create reference designators for given mbom item id.
    """
    create_reference_designator_body = {
        "query": queries.CREATE_MBOM_ITEM_REFERENCE_DESIGNATOR,
        "variables": {"input": {"mbomItemId": mbom_item_id, "value": value}},
    }
    api.request(create_reference_designator_body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add reference designators to existing mBOM item."
    )
    parser.add_argument("--client_id", type=str, help="Your API client ID")
    args = parser.parse_args()
    client_secret = getpass("Client secret: ")
    if not args.client_id or not client_secret:
        raise argparse.ArgumentError(
            "Must input client ID and " "client secret to run import"
        )
    api = Api(client_id=args.client_id, client_secret=client_secret)
    csv_data = CsvHelper.read_from_csv("add_reference_designators.csv")
    mbom_item_id = input("Enter the mBOM item ID: ")
    for index, row in enumerate(csv_data):
        if index == 0:
            continue
        print(f"Processing row {index}/{len(csv_data)}")
        add_reference_designator(api, mbom_item_id, row[0])
