"""
Updates attributes based on csv input script. Required inputs are issue_id, key, value.
Currently the only key being updated is "Defect Code", this can be modified to do more in the future. 
"""
import os
import sys
import inspect
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
    filename="delete_purchases/log.txt",
    filemode="w",
)

def get_issues(api):
    request_body = {"query": queries.GET_ISSUE_ATTRIBUTES}
    return api.request(request_body)["data"]

def update_issue_attribute(issues,api):
    file = open("issues.csv")
    csvreader = csv.reader(file)

    rows = []
    for row in csvreader:
        rows.append(row)
    file.close()

    for issue in issues["issues"]["edges"]:
        issue_id = issue["node"]["id"]
        for attribute_etag in issue["node"]["attributes"]:
            etag = attribute_etag["Etag"]
        for row in rows:
            if issue_id == int(row[0]):
                value = row[1]
            continue

    
        request_body = {
            "query": queries.UPDATE_ISSUE_ATTRIBUTE,
            "variables": {
                "input": {
                    "issueId": issue_id,
                    "key": "Defect Code",
                    "value": value,
                    "etag": etag
                }
            }
        }
        api.request(request_body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Use CSV to update custom attributes")
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
        issues = get_issues(ion_api)
        update_issue_attribute(issues,ion_api)

    except KeyError as e:
        print(f"KeyError occurred: {e}")
    except Exception as e:
        error = f"Error occurred while running script: {e}"
        print(error)
        logger.exception(error)
