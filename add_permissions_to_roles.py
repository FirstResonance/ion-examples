"""
Given a csv of roles and permissions, add permissions to roles (see add_permissions_to_roles.csv). 
"""

import argparse
from getpass import getpass
from utilities.api import Api
import queries
from utilities.csv_helper import CsvHelper


def attach_permission_group_to_role(api: Api, role_id: int, permission_group_id: int):
    """
    Add permission to role.
    """
    attach_permission_role_body = {
        "query": queries.ATTACH_PERMISSION_GROUP_TO_ROLE,
        "variables": {
            "input": {"roleId": role_id, "permissionGroupId": permission_group_id}
        },
    }
    api.request(attach_permission_role_body)


def get_permission_group_id(api: Api, permission_name) -> int:
    """
    Get permission group given name.
    """
    role_filter = {"name": {"eq": permission_name}}
    permission_groups_query = {
        "query": queries.GET_PERMISSION_GROUPS,
        "variables": {"filters": role_filter},
    }
    permission_groups = api.request(permission_groups_query)
    return permission_groups["data"]["permissionGroups"]["edges"][0]["node"]["id"]


def get_role_id(api: Api, role_name) -> int:
    """
    Get role given name.
    """
    role_filter = {"name": {"eq": role_name}}
    permission_groups_query = {
        "query": queries.GET_ROLES,
        "variables": {"filters": role_filter},
    }
    permission_groups = api.request(permission_groups_query)
    return permission_groups["data"]["roles"]["edges"][0]["node"]["id"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add permissions to existing roles from csv."
    )
    parser.add_argument("--client_id", type=str, help="Your API client ID")
    args = parser.parse_args()
    client_secret = getpass("Client secret: ")
    if not args.client_id or not client_secret:
        raise argparse.ArgumentError(
            "Must input client ID and " "client secret to run import"
        )
    api = Api(client_id=args.client_id, client_secret=client_secret)
    csv_data = CsvHelper.read_from_csv("add_permissions_to_roles.csv")
    for index, row in enumerate(csv_data):
        if index == 0:
            continue
        print(f"Processing row {index}/{len(csv_data)}")
        role_id = get_role_id(api, row[0])
        permission_group_id = get_permission_group_id(api, row[1])
        attach_permission_group_to_role(api, role_id, permission_group_id)
