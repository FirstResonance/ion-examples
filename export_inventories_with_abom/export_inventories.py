"""
Export a procedure from source environment to target environment. 
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
from utilities.csv_helper import CsvHelper
from config import config

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="export_inventories_with_abom/log.txt",
    filemode="w",
)


def get_inventories(api: Api):
    """Get inventories paginated 100 records at a time."""
    inventories = []
    query = """
        query GetInventories($after: String) {
            partInventories(first: 50, after: $after) {
                edges {
                    node {
                        part {
                            partNumber
                            description
                        }
                        serialNumber
                        lotNumber
                        buildRequirements {
                            abomInstallations {
                                quantity
                                partInventory {
                                    part {
                                        partNumber
                                        description
                                    }
                                    serialNumber
                                    lotNumber
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    """
    has_next_page = True
    after_id = None
    while has_next_page:
        request_body = {"query": query, "variables": {"after": after_id}}
        response = api.request(request_body)
        for inventory in response["data"]["partInventories"]["edges"]:
            for build_requirement in inventory["node"]["buildRequirements"]:
                for abom_installation in build_requirement["abomInstallations"]:
                    inventories.append({
                        "parentPartNumber": inventory["node"]["part"]["partNumber"],
                        "parentPartDescription": inventory["node"]["part"]["description"],
                        "serialNumber": inventory["node"]["serialNumber"],
                        "lotNumber": inventory["node"]["lotNumber"],
                        "childPartNumber": abom_installation["partInventory"]["part"]["partNumber"],
                        "childPartDescription": abom_installation["partInventory"]["part"]["description"],
                        "childSerialNumber": abom_installation["partInventory"]["serialNumber"],
                        "childLotNumber": abom_installation["partInventory"]["lotNumber"],
                    })
        has_next_page = response["data"]["partInventories"]["pageInfo"]["hasNextPage"]
        after_id = response["data"]["partInventories"]["pageInfo"]["endCursor"]
    return inventories


def export_inventories(inventories):
    """
    Exports inventories to csv.
    """
    CsvHelper.write_to_csv(inventories, "export_inventories_with_abom/inventories.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate a procedure from one environment to another."
    )
    try:
        auth_server = config["ION_AUTH_SERVER"]
        api_uri = config["ION_API_URI"]
        client_id = config["ION_CLIENT_ID"]
        client_secret = config["ION_CLIENT_SECRET"]
    except Exception as e:
        raise (f"Error: missing config settings: {e}")

    try:
        api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
            logger=logger,
        )
        inventories = get_inventories(api)
        export_inventories(inventories)

        print("Completed exporting inventories.")
    except Exception as e:
        error = f"Error occurred while exporting inventories: {e}"
        print(error)
        logger.exception(error)
