"""
Bulk delete labels from runs. 
"""
import csv
import argparse
import queries
from utilities.api import Api
from config import config

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="bulk_delete_labels_from_runs/log.txt",
    filemode="w",
)

# Assumes id,label,boat headers in the csv
RUNS_FILE = "bulk_delete_labels_from_runs/runs.csv"


def read_csv_as_dicts(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [row for row in reader]


def queryRun(run_id):
    query_input = {"id": run_id}
    request_body = {"query": queries.GET_RUN_ENTITY_LABELS, "variables": query_input}
    res = api.request(request_body)
    return res["data"]["run"]


def getRuns(data):
    return [{"run": queryRun(run["id"]), "data": run} for run in data]


def delete_all_labels_from_runs(runs_data):
    for run_data in runs_data:
        run = run_data["run"]
        for label in run["labels"]:
            mutation_input = {
                "input": {"entityId": run["entityId"], "labelId": label["id"]}
            }
            request_body = {
                "query": queries.REMOVE_LABEL_TO_ITEM,
                "variables": mutation_input,
            }
            try:
                api.request(request_body)
            except Exception as e:
                logger.info(e)


def get_label(value: str):
    """Check if label already exists and if not, create it."""
    request_body = {
        "query": queries.GET_LABELS,
        "variables": {"filters": {"value": {"eq": value}}},
    }
    existing_labels = api.request(request_body)["data"]["labels"]["edges"]
    if existing_labels:
        return existing_labels[0]["node"]
    else:
        new_label_request_body = {
            "query": queries.CREATE_LABEL,
            "variables": {"input": {"value": value}},
        }
        new_label = api.request(new_label_request_body)["data"]

        return new_label["createLabel"]["label"]


def create_or_get_labels(labels):
    return {label: get_label(label) for label in labels}


def add_labels_to_runs(runs_data, labels_data):
    for run_data in runs_data:
        run = run_data["run"]
        label_value_to_assign = run_data["data"]["label"]
        label_to_assign = labels_data[label_value_to_assign]

        mutation_input = {
            "input": {"entityId": run["entityId"], "labelId": label_to_assign["id"]}
        }
        request_body = {"query": queries.ADD_LABEL_TO_ITEM, "variables": mutation_input}
        try:
            api.request(request_body)
        except Exception as e:
            logger.info(e)


def update_boat_attribute_to_runs(runs_data):
    for run_data in runs_data:
        run = run_data["run"]
        data = run_data["data"]
        mutation_input = {
            "input": {
                "etag": run["_etag"],
                "key": "Boat",
                "runId": run["id"],
                "value": data["boat"],
            }
        }
        request_body = {
            "query": queries.UPDATE_RUN_ATTRIBUTE,
            "variables": mutation_input,
        }
        try:
            api.request(request_body)
        except Exception as e:
            logger.info(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add users to existing teams from csv."
    )
    try:
        auth_server = config["ION_AUTH_SERVER"]
        api_uri = config["ION_API_URI"]
        client_id = config["ION_CLIENT_ID"]
        client_secret = config["ION_CLIENT_SECRET"]
    except Exception as e:
        raise (f"Error with the config settings: {e}")

    api = Api(
        auth_server=auth_server,
        api_uri=api_uri,
        client_id=client_id,
        client_secret=client_secret,
        logger=logger,
    )

    data = read_csv_as_dicts(RUNS_FILE)

    runs_data = getRuns(data)

    delete_all_labels_from_runs(runs_data)

    distinct_labels = {run_data["data"]["label"] for run_data in runs_data}

    label_data = create_or_get_labels(distinct_labels)

    add_labels_to_runs(runs_data, label_data)

    update_boat_attribute_to_runs(runs_data)
