import pandas as pd
import numpy as np
from getpass import getpass
from utilities.api import Api
import argparse
from datetime import date
import queries
import os

API_URL = "https://api.buildwithion.com"
AUTHENTICATION_SERVER = "auth.buildwithion.com"

Loc = 301

def get_inv(loc, api):
    query = {
        'query': queries.GET_PART_INVENTORIES,
        'variables': {
            'filters': {
                "locationId": {"eq": loc},
                "status": {"neq": "INSTALLED"}
            }
        }
    }
    r = api.request(query)
    num = len(r['data']['partInventories']['edges'])
    d_list = [r['data']['partInventories']['edges'][i]['node'] for i in range(num)]
    df = pd.DataFrame.from_records(d_list)
    df = pd.concat([df.drop(['part'], axis=1), df['part'].apply(pd.Series)], axis=1)
    df = df.drop(['id', 'quantityAvailable'], axis=1)
    gp_df = df.groupby(['partId', 'partNumber']).agg({'quantity': 'sum'}).reset_index()
    gp_df['floor_count'] = ""
    dat = date.today()
    d4 = dat.strftime("%d.%m.%Y")
    home_directory = os.path.expanduser('~')
    gp_df.to_csv(os.path.join(home_directory, f'hardware_audit_{d4}.csv'), index=False)
    print('Inventory has been downloaded!')

if __name__ == "__main__":
    client_id = '9d5aeee2-da60-45ad-ab00-3e50a9ee32ff'
    client_secret = getpass("Client secret: ")
    if not client_id or not client_secret:
        raise ValueError("Must input client ID and client secret to run import")
    api = Api(client_id=client_id, client_secret=client_secret)
    get_inv(loc=Loc, api=api)
