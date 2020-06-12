import requests

from financial.apps.scraping.exceptions import InvalidResponse
from .properties import (
    props,
    URL_BASE,
)


class ScrapingServices:

    def get_nemos(self):
        uri = props['nemo_uri']

        response = requests.post(
            url=f'{URL_BASE}{uri}',
            headers=props['headers'],
            json={},
            verify=False,
        )

        if not response.ok:
            raise InvalidResponse

        return response.json()
