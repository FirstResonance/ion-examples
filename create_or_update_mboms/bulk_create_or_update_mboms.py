"""
Bulk create or update mBOMs from a csv. 
"""
import os
import sys
import inspect

# Reset the path so it can be run from the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import argparse # noqa: E402
from utilities.api import Api  # noqa: E402
from utilities.csv_helper import CsvHelper # noqa: E402
import queries # noqa: E402
from config import config # noqa: E402
import logging # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="create_or_update_mboms/log.txt",
    filemode="w",
)


def create_or_update_mboms(api: Api, input_list: list[dict], is_level_notation: bool = False):
    """Create or update mboms."""
    notation_var: bool = "levelInputs" if is_level_notation else "depthInputs"
    request_body = {
        "query": queries.CREATE_OR_UPDATE_MBOMS,
        "variables": {
            "input": {
                "importerType": "LEVEL" if is_level_notation else "DEPTH",
                notation_var: input_list
            }
        },
    }
    res = api.request(request_body)
    logger.info(f"Response: {res}")
    return res["data"]["createOrUpdateMultipleMboms"]

def convert_csv_rows_into_json(csv_data: list, is_level_notation: bool = False) -> list[dict]:
    items_length: int = len(csv_data) - 1
    logger.info(f"{items_length} mBOM items to process.")
    input_list: list[dict] = []
    for index, row in enumerate(csv_data):
        if index == 0:
            continue
        logger.info(f"Processing row {index}/{items_length}")
        mbom_notation: str = "level" if is_level_notation else "depth"
        input_list.append({
            mbom_notation: row[0] if is_level_notation else int(row[0]),
            "partNumber": row[1],
            "revision": row[2],
            "quantity": float(row[3]),
            "substitutes": row[4],
            "madeOnAssembly": row[5].strip().lower() == "true"
        })
    logger.info(f"Input list: {input_list}")
    return input_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create and update mBOMs."
    )
    parser.add_argument('--level', action='store_true', help='Use level notation for mBOM upload.')
    args = parser.parse_args()
    try:
        auth_server = config["ION_AUTH_SERVER"]
        api_uri = config["ION_API_URI"]
        client_id = config["ION_CLIENT_ID"]
        client_secret = config["ION_CLIENT_SECRET"]
    except Exception as e:
        print(f"Error with the config settings: {e}")
        raise (e)

    try:
        api = Api(
            client_id=client_id,
            client_secret=client_secret,
            auth_server=auth_server,
            api_uri=api_uri,
            logger=logger,
        )
        csv_file_path: str = "create_or_update_mboms/create_or_update_mboms_depth.csv"
        if args.level:
            csv_file_path = "create_or_update_mboms/create_or_update_mboms_level.csv"
        csv_data: list = CsvHelper.read_from_csv(csv_file_path)
        logger.info(csv_data)
        json_data: list[dict] = convert_csv_rows_into_json(csv_data, args.level)
        logger.info(json_data)
        resp: dict = create_or_update_mboms(api, json_data, args.level)
        logger.info(resp)
        if len(resp["errorMessages"]) > 0:
            logger.info("There were some errors in the CSV file as noted below:")
            for error in resp["errorMessages"]:
                logger.info(f"In row {error['rowId']}: {error['errorMsg']}")
        else:
            logger.info(f"Following mBOMs were created: {', '.join([str(id) for id in resp['newMbomRowIds']])}")
        logger.info("Completed creates or updates of mBOMs.")
    except Exception as e:
        logger.info(f"Error occurred while running script: {e}")
        raise (e)
