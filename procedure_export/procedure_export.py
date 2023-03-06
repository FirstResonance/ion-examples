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
            "attributes": source_procedure_data["attributes"],
        },
    }
    new_procedure = api.request(request_body)["data"]["createProcedure"]["procedure"]
    logger.info(f"New procedure {new_procedure}")
    return new_procedure


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


def add_field_to_step(api: Api, field: dict, step_id: int):
    input = field
    field["stepId"] = step_id
    # remove nulls
    for key, value in list(input.items()):
        if value == None or key in ["id", "validations"]:
            del input[key]
    request_body = {
        "query": queries.CREATE_STEP_FIELD,
        "variables": {"input": input},
    }
    api.request(request_body)


def add_datagrid_to_step(api: Api, columns: dict, rows: dict, step_id: int):
    column_map = {}
    for column in columns["edges"]:
        column_input = column["node"].copy()
        column_input["stepId"] = step_id
        del column_input["id"]
        column_body = {
            "query": queries.CREATE_DATAGRID_COLUMN,
            "variables": {"input": column_input},
        }
        new_column = api.request(column_body)["data"]["createDatagridColumn"][
            "datagridColumn"
        ]
        column_map[column["node"]["id"]] = new_column["id"]
    for row in rows["edges"]:
        rows_input = row["node"].copy()
        rows_input["stepId"] = step_id
        del rows_input["values"]
        del rows_input["id"]
        rows_body = {
            "query": queries.CREATE_DATAGRID_ROW,
            "variables": {"input": rows_input},
        }
        new_row = api.request(rows_body)["data"]["createDatagridRow"]["datagridRow"]
        for value in row["node"]["values"]:
            value_body = {
                "query": queries.SET_DATAGRID_VALUE,
                "variables": {
                    "input": {
                        "rowId": new_row["id"],
                        "columnId": column_map[value["columnId"]],
                        "value": value["value"],
                    }
                },
            }
            api.request(value_body)


def find_existing_standard_step(api: Api, title: str):
    request_body = {
        "query": queries.GET_STEPS,
        "variables": {"filters": {"title": {"eq": title}}},
    }
    existing_steps = api.request(request_body)["data"]["steps"]["edges"]
    if existing_steps:
        return existing_steps[0]["node"]


def load_standard_step(source_api: Api, id: int):
    request_body = {
        "query": queries.GET_STEP,
        "variables": {"id": id},
    }
    standard_step = source_api.request(request_body)["data"]["step"]
    return standard_step


def add_step(
    api: Api,
    step: dict,
    source_procedure_data: dict,
    procedure_id: int,
    source_api: Api,
    step_map: dict,
    parent_step_id: int = None,
    is_standard_step: bool = False,
):
    if is_standard_step:
        import pdb

        pdb.set_trace()
    create_step_input = {
        "slateContent": step["slateContent"],
        "title": step["title"],
        "procedureId": procedure_id,
        "leadTime": step["leadTime"],
        "locationId": step["locationId"],
        "locationSubtypeId": step["locationSubtypeId"],
        "type": step["type"],
        "parentId": parent_step_id,
    }
    if is_standard_step:
        del create_step_input["procedureId"]
    request_body = {
        "query": queries.CREATE_STEP,
        "variables": {"input": create_step_input},
    }
    new_step = api.request(request_body)["data"]["createStep"]["step"]
    step_map[step["id"]] = new_step["id"]
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
    for field in step["fields"]:
        add_field_to_step(api, field, new_step["id"])
    # Add child steps
    if not parent_step_id:
        for child_step in step["steps"]:
            add_step(
                api,
                child_step,
                source_procedure_data,
                procedure_id,
                source_api,
                step_map,
                new_step["id"],
                is_standard_step=is_standard_step,
            )
    # Create data grid
    if step["type"] == "DATAGRID":
        add_datagrid_to_step(
            api, step["datagridColumns"], step["datagridRows"], new_step["id"]
        )
    return new_step


def add_dependencies(api: Api, step_map: dict, dependencies: dict):
    for step_id, upstream_step_id in dependencies.items():
        value_body = {
            "query": queries.CREATE_STEP_EDGE,
            "variables": {
                "stepId": step_map[step_id],
                "upstreamStepId": step_map[upstream_step_id],
            },
        }
        api.request(value_body)


def copy_step_into_procedure(api: Api, step_id: int, procedure_id: int):
    body = {
        "query": queries.COPY_STEP,
        "variables": {"input": {"procedureId": procedure_id, "stepId": step_id}},
    }
    new_step = api.request(body)["data"]["copyStep"]["step"]
    return new_step


def add_steps(
    api: Api, source_procedure_data: dict, procedure_id: int, source_api: Api
):
    """Adds steps to newly created procedure."""
    logger.info(f"Adding {len(source_procedure_data['steps'])} step to procedure")
    step_map = {}
    dependencies = {}
    for step in source_procedure_data["steps"]:
        for upstream_step_id in step["upstreamStepIds"]:
            dependencies[step["id"]] = upstream_step_id
        if step["isDerivedStep"]:
            reference_standard_step = find_existing_standard_step(api, step["title"])
            if not reference_standard_step:
                standard_step = load_standard_step(source_api, step["originStepId"])
                reference_standard_step = add_step(
                    api,
                    standard_step,
                    source_procedure_data,
                    procedure_id,
                    source_api,
                    step_map,
                    is_standard_step=True,
                )
            derived_step = copy_step_into_procedure(
                api, reference_standard_step["id"], procedure_id
            )
            step_map[step["id"]] = derived_step["id"]
        else:
            add_step(
                api, step, source_procedure_data, procedure_id, source_api, step_map
            )
        add_dependencies(api, step_map, dependencies)


def get_label(api: Api, value: str):
    # first check if the label already exists
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


def add_labels(api: Api, labels: list, procedure_family_id: int):
    for label in labels:
        logger.info(f"Adding {label} label to procedure.")
        new_label = get_label(api, label)
        request_body = {
            "query": queries.ADD_LABEL_TO_PROCEDURE_FAMILY,
            "variables": {
                "input": {"labelId": new_label["id"], "familyId": procedure_family_id}
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
        raise (f"Error occurred while exporting procedure: {e}")
