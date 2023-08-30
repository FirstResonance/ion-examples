import os
import sys
import inspect

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

QUERYLOCATIONSMUTATION = '''
query locations($filters:LocationsInputFilters)
{
  locations (filters:$filters) {
    edges {
      node {
        id
        _etag
      }
    }
  }
}
'''

DELETELOCATIONMUTATION='''
mutation DeleteLocation($id:ID!, $etag:String!) {
  deleteLocation(id:$id,etag:$etag)
  {
    id
  }
}
  '''

def get_locations(api):
  request_body = {"query": QUERYLOCATIONSMUTATION}
  return api.request(request_body)["data"]

def delete_locations(locations,api):
  for location in locations["locations"]["edges"]:
    receipt_id = location["node"]["id"]
    etag = location["node"]["_etag"]
    request_body = {
      "query": DELETELOCATIONMUTATION,
      "variables": {"id": receipt_id, "etag": etag},
    }
    api.request(request_body)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk delete locations.")
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
        locations = get_locations(ion_api)
        delete_locations(locations, ion_api)
    except Exception as e:
        error = f"Error occurred while running script: {e}"
        print(error)
        logger.exception(error)