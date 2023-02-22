"""
Get all available permission groups from ION. 
"""

import argparse
from getpass import getpass
from utilities.api import Api
from utilities.csv_helper import CsvHelper
import queries


def get_all_permission_groups(api: Api) -> list:
    """
    Gets all permission groups that exist within ION.
    """
    permission_groups_query = {
        "query": queries.GET_PERMISSION_GROUPS,
    }
    permission_groups = api.request(permission_groups_query)
    return [
        permission_group["node"]
        for permission_group in permission_groups["data"]["permissionGroups"]["edges"]
    ]


def write_to_csv(permission_groups):
    CsvHelper.write_to_csv(permission_groups, "permission_groups.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get all ION permission groups.")
    parser.add_argument("--client_id", type=str, help="Your API client ID")
    args = parser.parse_args()
    client_secret = getpass("Client secret: ")
    if not args.client_id or not client_secret:
        raise argparse.ArgumentError(
            "Must input client ID and " "client secret to run import"
        )
    api = Api(client_id=args.client_id, client_secret=client_secret)
    permission_groups = get_all_permission_groups(api)
    write_to_csv(permission_groups)
