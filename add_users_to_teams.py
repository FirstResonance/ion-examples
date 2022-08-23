"""
Given a csv of user emails and teams, add users to teams (see add_users_to_teams.csv). 
"""

import argparse
from getpass import getpass
from utilities.api import Api
import queries
from utilities.csv_helper import CsvHelper


def add_user_to_team(api: Api, team_id: int, user_id: int):
    """
    Add a user to a team.
    """
    add_user_to_team_body = {
        'query': queries.ADD_USER_TO_TEAM,
        'variables': {'input': {
            'userId': user_id,
            'teamId': team_id
        }}
    }
    api.request(add_user_to_team_body)

def get_team_id(api: Api, team_name) -> int:
    """
    Get team Id from team name.
    """
    team_filter = {
        'name': {
            'eq': team_name
        }
    }
    teams_query = {
        'query': queries.GET_TEAMS,
        'variables': {
            'filters': team_filter
        }
    }
    teams = api.request(teams_query)
    return teams['data']['teams']['edges'][0]['node']['id']

def get_user_id(api: Api, user_email) -> int:
    """
    Get user Id from user email.
    """
    user_filter = {
        'email': {
            'eq': user_email
        }
    }
    users_query = {
        'query': queries.GET_USERS,
        'variables': {
            'filters': user_filter
        }
    }
    users = api.request(users_query)
    return users['data']['users']['edges'][0]['node']['id']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Add users to existing teams from csv.')
    parser.add_argument('--client_id', type=str, help='Your API client ID')
    args = parser.parse_args()
    client_secret = getpass('Client secret: ')
    if not args.client_id or not client_secret:
        raise argparse.ArgumentError('Must input client ID and '
                                     'client secret to run import')
    api = Api(client_id=args.client_id, client_secret=client_secret)
    csv_data = CsvHelper.read_from_csv('add_users_to_teams.csv')
    for index, row in enumerate(csv_data):
        if index == 0:
            continue
        print(f'Processing row {index}/{len(csv_data)}')
        team_id = get_team_id(api, row[0])
        user_id = get_user_id(api, row[1])
        add_user_to_team(api, team_id, user_id)
