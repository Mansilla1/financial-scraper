import requests

from copy import deepcopy
from json.decoder import JSONDecodeError

from financial.apps.scraping.exceptions import (
    InvalidCSRFToken,
    InvalidResponse,
)
from .properties import (
    props,
    URL_BASE,
)


class ScrapingServices:

    def __init__(self):
        self._session = requests.Session()

    def _get_csrf_token(self):
        csrf_url = props['uri']['csrf']

        try:
            csrf_response = self._session.get(
                url=f'{URL_BASE}{csrf_url}',
                verify=False,
            )

            if not csrf_response.ok:
                raise InvalidCSRFToken

            csrf_token = csrf_response.json()['csrf']
        except (JSONDecodeError, KeyError):
            raise InvalidCSRFToken

        return csrf_token

    def get_nemos(self):
        uris = props['uri']
        nemos = uris['nemos']

        headers = deepcopy(props['headers'])
        headers['X-CSRF-Token'] = self._get_csrf_token()

        response = self._session.post(
            url=f'{URL_BASE}{nemos}',
            headers=headers,
            json={},
            verify=False,
        )

        if not response.ok:
            raise InvalidResponse

        try:
            json_result = response.json()
            result = {
                'nemos': json_result['listaResult'],
            }
        except (JSONDecodeError, KeyError):
            result = []

        return result
