import os
import json
import requests
from urllib.parse import urljoin

AUTH0_DOMAIN = 'firstresonance.auth0.com'
API_URL = os.getenv('ION_API_URI', 'https://api.firstresonance.io/')


class Api(object):
    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = os.getenv(
            'ION_API_AUDIENCE', 'https://trial-api.firstresonance.io/')
        self.access_token = self.get_access_token()

    def get_access_token(self) -> str:
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': self.audience,
            'grant_type': 'client_credentials'
        }

        headers = {'content-type': 'application/json'}

        auth_url = urljoin(f'https://{AUTH0_DOMAIN}', 'oauth/token')
        res = requests.post(auth_url, json=payload, headers=headers)
        return res.json()['access_token']

    def _get_headers(self) -> dict:
        """
        Get API request headers.

        Returns:
            dict: Return API request headers with authorization token.
        """
        return {'Authorization': f'{self.access_token}',
                'Content-Type': 'application/json'}

    def request(self, query_info: dict) -> dict:
        """
        Send authenticated request to ION GraphQL API.

        Args:
            query_info (dict): Mutation or resolver request info.

        Returns:
            dict: API response from request.
        """
        headers = self._get_headers()
        res = requests.post(urljoin(API_URL, 'graphql'), headers=headers, json=query_info)
        resp_value = res.json()
        if resp_value.get('errors'):
            print('---AN ERROR OCCURRED IN THE API REQUEST---')
            print(resp_value)
        return resp_value
