import requests

from copy import deepcopy
from json.decoder import JSONDecodeError
from typing import List

from financial.apps.scraping.exceptions import (
    InvalidCSRFToken,
    InvalidResponse,
)
from .properties import (
    props,
    URL_BASE,
)
from financial.apps.scraping.models import NemotechModel


class ScrapingServices:

    def __init__(self):
        self._session = requests.Session()

    def _get_csrf_token(self) -> str:
        """
        Get csrf token of base url page
        :return: string
        """
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

    def get_nemos(self, save=False) -> List[dict]:
        """
        Scraping nemos of page and save it in database
        :param save: boolean, default False
        :return result: list of dictionaries
        """
        uris = props['uri']
        nemos = uris['nemos']

        headers = deepcopy(props['headers'])
        headers['X-CSRF-Token'] = self._get_csrf_token()

        response = self._session.post(
            url=f'{URL_BASE}{nemos}',
            headers=headers,
            verify=False,
        )

        if not response.ok:
            raise InvalidResponse

        try:
            mapped_keys = props['mapping_values']['nemos']
            json_result = response.json()['listaResult']

            result = [
                {
                    mapped_keys[_key]: _value
                    for _key, _value in _result.items()
                    if _key in mapped_keys.keys()
                }
                for _result in json_result
            ]
        except (JSONDecodeError, KeyError):
            result = []

        if save and result:
            NemotechModel.objects.bulk_insert(result)

        return result
