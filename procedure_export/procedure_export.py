"""
Export a procedure from source environment to target environment. 
"""
import os
import sys
import inspect
import re
import json


# Reset the path so it can be run from the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import argparse
from utilities.api import Api
from utilities.file_attachment_helper import FileAttachmentHelper
import queries
from config import config

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="procedure_export/log.txt",
    filemode="w",
)

file_attachment_helper = FileAttachmentHelper()


def get_procedure_data(api: Api, procedure_id: int):
    """Get procedure info given procedure id."""
    request_body = {"query": queries.GET_PROCEDURE, "variables": {"id": procedure_id}}
    return api.request(request_body)["data"]["procedure"]


def create_procedure_container(api: Api, source_procedure_data: dict, new_title: str):
    """Create new procedure."""
    request_body = {
        "query": queries.CREATE_PROCEDURE,
        "variables": {
            "title": new_title or source_procedure_data["title"],
            "description": source_procedure_data["description"],
            "type": source_procedure_data["type"],
        },
    }
    return api.request(request_body)["data"]["createProcedure"]["procedure"]


def create_ion_file_attachment(api: Api, file_name: str, step_entity_id: int):
    """Create new file attachment in ION."""
    request_body = {
        "query": queries.CREATE_ASSET,
        "variables": {"input": {"filename": file_name, "entityId": step_entity_id}},
    }
    return api.request(request_body)["data"]["createAsset"]


def add_asset(api: Api, asset: dict, step: dict):
    """Download file from source env, upload to target, and add as asset on the step."""
    file_name = asset["filename"]
    file_object = file_attachment_helper.download_file_attachment(
        asset["downloadUrl"], asset["filename"]
    )
    new_file_attachment = create_ion_file_attachment(api, file_name, step["entityId"])
    file_attachment_helper.upload_file_attachment(
        file_object, file_name, new_file_attachment
    )
    return new_file_attachment


def get_file_attachment_info(api: Api, file_attachment_id: int):
    """Get info for given file attachment id."""
    request_body = {
        "query": queries.GET_FILE_ATTACHMENT,
        "variables": {"id": file_attachment_id},
    }
    return api.request(request_body)["data"]["fileAttachment"]


def update_step_slate_content(
    api: Api, etag: str, step_id: str, new_slate_content: str
):
    """Update step slate content."""
    request_body = {
        "query": queries.UPDATE_STEP,
        "variables": {
            "input": {"id": step_id, "etag": etag, "slateContent": new_slate_content}
        },
    }
    return api.request(request_body)


def add_steps(
    api: Api, source_procedure_data: dict, procedure_id: int, source_api: Api
):
    """Adds steps to newly created procedure."""
    logger.info(f"Adding {len(source_procedure_data['steps'])} step to procedure")
    for step in source_procedure_data["steps"]:
        request_body = {
            "query": queries.CREATE_STEP,
            "variables": {
                "input": {
                    "slateContent": step["slateContent"],
                    "title": step["title"],
                    "procedureId": procedure_id,
                    "leadTime": step["leadTime"],
                    "locationId": step["locationId"],
                    "locationSubtypeId": step["locationSubtypeId"],
                    "type": step["type"],
                }
            },
        }
        new_step = api.request(request_body)["data"]["createStep"]["step"]
        logger.info(f"Added new step: {new_step}")
        # Skipping adding step assets for now b/c it gets handled below in the slate content
        # logger.info(f"Transitioning {len(step['assets'])} step assets.")
        # for asset in step["assets"]:
        #     new_file_attachment = add_asset(api, asset, new_step)
        # replace any references to old file attachment in step content
        logger.info(f"Replacing step slate content references to file attachments")
        slate_content = step["slateContent"]
        if slate_content:
            expression = "reference.: (?P<id>\d*), "
            # Need to convert first to a string (json.dumps) so the text can be replaced.
            # Uses a regex match to find all references
            for match in re.finditer(expression, json.dumps(slate_content)):
                # Getting existing file attachment data
                existing_file_attachment = get_file_attachment_info(
                    source_api, match.groupdict()["id"]
                )
                # Uploading file to target env
                new_file_attachment = add_asset(api, existing_file_attachment, new_step)
                # Replace slate content references
                new_slate_content = json.dumps(slate_content).replace(
                    match.group(),
                    f"reference\": {new_file_attachment['fileAttachment']['id']}, ",
                )
                update_step_slate_content(
                    api,
                    new_step["_etag"],
                    new_step["id"],
                    json.loads(new_slate_content),
                )

def get_label(api: Api, value: str):
    # first check if the label already exists
    request_body = {
            "query": queries.GET_LABELS,
            "variables": {
                "filters": {
                    "value": {
                        "eq": value
                    }
                }
            },
        }
    existing_labels = api.request(request_body)["data"]["labels"]["edges"]
    if existing_labels:
        return existing_labels[0]["node"]
    else:
        new_label_request_body = {
            "query": queries.CREATE_LABEL,
            "variables": {
                "input": {
                    "value": value
                }
            }
        }
        new_label = api.request(new_label_request_body)["data"]
        return new_label["createLabel"]["label"]

def add_labels(api: Api, labels: list, procedure_family_id: int):
    for label in labels:
        logger.info(f"Adding {label} label to procedure.")
        new_label = get_label(api, label)
        request_body = {
            "query": queries.ADD_LABEL_TO_PROCEDURE_FAMILY,
            "variables": {
                "input": {
                    "labelId": new_label["id"],
                    "familyId": procedure_family_id
                }
            },
        }
        api.request(request_body)["data"]
    

def create_procedure_from_source_data(
    api: Api, source_procedure_data: dict, new_title: str, source_api: Api
):
    """
    Create new procedure in target environment from source data.
    """
    new_procedure = create_procedure_container(api, source_procedure_data, new_title)
    labels = source_procedure_data["labels"]
    add_labels(api, labels, new_procedure["familyId"])
    new_procedure_id = new_procedure["id"]
    logger.info(f"Created new procedure: {new_procedure_id}")
    new_steps = add_steps(api, source_procedure_data, new_procedure_id, source_api)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate a procedure from one environment to another."
    )
    try:
        source_auth_server = config["SOURCE_ION_AUTH_SERVER"]
        source_api_uri = config["SOURCE_ION_API_URI"]
        source_client_id = config["SOURCE_ION_CLIENT_ID"]
        source_client_secret = config["SOURCE_ION_CLIENT_SECRET"]
        target_auth_server = config["TARGET_ION_AUTH_SERVER"]
        target_api_uri = config["TARGET_ION_API_URI"]
        target_client_id = config["TARGET_ION_CLIENT_ID"]
        target_client_secret = config["TARGET_ION_CLIENT_SECRET"]
    except Exception as e:
        raise (f"Error with the config settings: {e}")

    try:
        source_api = Api(
            client_id=source_client_id,
            client_secret=source_client_secret,
            auth_server=source_auth_server,
            api_uri=source_api_uri,
        )
        target_api = Api(
            client_id=target_client_id,
            client_secret=target_client_secret,
            auth_server=target_auth_server,
            api_uri=target_api_uri,
        )
        procedure_id = input("Input the procedure ID that you would like to export: ")
        new_title = input("Enter an optional title for the new procedure: ")
        procedure_data = get_procedure_data(source_api, procedure_id)
        create_procedure_from_source_data(
            target_api, procedure_data, new_title, source_api
        )
        print("Completed procedure export.")
    except Exception as e:
        raise(f"Error occurred while exporting procedure: {e}")
