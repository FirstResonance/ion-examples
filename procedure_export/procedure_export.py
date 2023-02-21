"""
Export a procedure from source environment to target environment. 
"""
import os
import sys
import inspect
import re
import json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import argparse
from utilities.api import Api
from utilities.file_attachment_helper import FileAttachmentHelper
import queries
from config import config

file_attachment_helper = FileAttachmentHelper()


def get_procedure_data(api: Api, procedure_id: int):
    """
    Get procedure info for given mbom item id.
    """
    request_body = {"query": queries.GET_PROCEDURE, "variables": {"id": procedure_id}}
    return api.request(request_body)["data"]["procedure"]


def create_procedure_container(api: Api, source_procedure_data: dict, new_title: str):
    request_body = {
        "query": queries.CREATE_PROCEDURE,
        "variables": {
            "title": new_title or source_procedure_data["title"],
            "description": source_procedure_data["description"],
            "type": source_procedure_data["type"],
        },
    }
    return api.request(request_body)


def create_ion_file_attachment(api: Api, file_name: str, step_entity_id: int):
    request_body = {
        "query": queries.CREATE_ASSET,
        "variables": {"input": {"filename": file_name, "entityId": step_entity_id}},
    }
    return api.request(request_body)["data"]["createAsset"]


def add_asset(api: Api, asset: dict, step: dict):
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
    request_body = {
        "query": queries.GET_FILE_ATTACHMENT,
        "variables": {"id": file_attachment_id},
    }
    return api.request(request_body)["data"]["fileAttachment"]


def update_step_slate_content(
    api: Api, etag: str, step_id: str, new_slate_content: str
):
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
        # Add file attachments
        slate_content = step["slateContent"]
        for asset in step["assets"]:
            new_file_attachment = add_asset(api, asset, new_step)
        # replace any references to old file attachment in step content
        if slate_content:
            expression = "reference.: (?P<id>\d*), "
            for match in re.finditer(expression, json.dumps(slate_content)):
                existing_file_attachment = get_file_attachment_info(
                    source_api, match.groupdict()["id"]
                )
                new_file_attachment = add_asset(api, asset, new_step)
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


def create_procedure_from_source_data(
    api: Api, source_procedure_data: dict, new_title: str, source_api: Api
):
    """
    Create new procedure in target environment from source data.
    """
    new_procedure = create_procedure_container(api, source_procedure_data, new_title)
    new_procedure_id = new_procedure["data"]["createProcedure"]["procedure"]["id"]
    new_steps = add_steps(api, source_procedure_data, new_procedure_id, source_api)
    print(f"New procedure: {new_procedure_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate a procedure from one environment to another."
    )
    source_auth_server = config["SOURCE_ION_AUTH_SERVER"]
    source_api_uri = config["SOURCE_ION_API_URI"]
    source_client_id = config["SOURCE_ION_CLIENT_ID"]
    source_client_secret = config["SOURCE_ION_CLIENT_SECRET"]
    target_auth_server = config["TARGET_ION_AUTH_SERVER"]
    target_api_uri = config["TARGET_ION_API_URI"]
    target_client_id = config["TARGET_ION_CLIENT_ID"]
    target_client_secret = config["TARGET_ION_CLIENT_SECRET"]
    # do a check on config variables
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
    create_procedure_from_source_data(target_api, procedure_data, new_title, source_api)
