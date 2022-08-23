import os
import logging
import requests
from urllib.parse import urljoin

AUTH0_DOMAIN = os.getenv('ION_AUTH_SERVER', 'staging-auth.buildwithion.com')
API_URL = os.getenv('ION_API_URI', 'https://staging-api.buildwithion.com')


class Api(object):
    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = os.getenv(
            'ION_API_AUDIENCE', API_URL)
        self.access_token = self.get_access_token()

    def get_access_token(self) -> str:
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': self.audience,
        }

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        auth_url = urljoin(f'https://{AUTH0_DOMAIN}', '/auth/realms/api-keys/protocol/openid-connect/token', 'oauth/token')
        res = requests.post(auth_url, data=payload, headers=headers)
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
            logging.error('---AN ERROR OCCURRED IN THE API REQUEST---')
            logging.error(resp_value)
        return resp_value
