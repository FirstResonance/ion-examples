"""
This script shows how to get the steps in a run and attach a file to
that run. In this example, we are simply uploading the file to the first step
in the run. In application, you will want to identify the step by title or position
and upload the file to that step accordingly.

The ion file code flow is the following:
1. Get a pre-signed secure URL from the ion API
2. Upload file to the S3 location at the secure URL using HTTP PUT
"""


import argparse
from getpass import getpass
import os
import requests
from utilities.api import Api
import queries
from config import config


def upload_file_to_step(api: Api, run_id: int, file_path: str) -> bool:
    """
    Finds a run by the provided run ID and uploads the provided file
    to the first step of that run.

    Args:
        api (Api): API instance to send authenticated requests
        file_path (str): The path of the file to upload to the step

    Returns:
        bool: True if the upload succeeded
    """
    # Get the run you want to upload to, so we can find the step to upload to
    r = api.request({"query": queries.GET_RUN, "variables": {"id": run_id}})
    run = r["data"]["run"]
    first_step = run["steps"][0]

    # Get the target URL we can upload our file to by using the
    # createFileAttachment API mutation. We are making the request against
    # the step's entityId, which is how files are associated to objects in ion
    attachment_data = {
        "input": {
            "entityId": first_step["entityId"],
            "filename": os.path.basename(file_path),
        }
    }
    upload_request = api.request(
        {"query": queries.CREATE_FILE_ATTACHMENT, "variables": attachment_data}
    )
    url = upload_request["data"]["createFileAttachment"]["uploadUrl"]

    # Now, let's upload the file!
    headers = {'Content-Type': upload_request["data"]["createFileAttachment"]["fileAttachment"]["contentType"]}
    
    r = requests.put(url,headers=headers,data=open(file_path, "rb"))
    return r.ok

if __name__ == "__main__":
    auth_server = config["ION_AUTH_SERVER"]
    api_uri = config["ION_API_URI"]
    client_id = config["ION_CLIENT_ID"]
    client_secret = config["ION_CLIENT_SECRET"]
    parser = argparse.ArgumentParser(
        description="Upload a file to the first step in a run"
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="The path of the file you want to upload to the step.",
    )
    ion_api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
        )
    if not client_id or not client_secret:
        raise argparse.ArgumentError(
            "Must input client ID and " "client secret to run import"
        )
    parser.add_argument("run_id", type=str, help="The run to upload the file to.")
    args = parser.parse_args()
    api = Api(client_id=client_id, client_secret=client_secret)
    upload_file_to_step(api, args.run_id, args.file_path)
