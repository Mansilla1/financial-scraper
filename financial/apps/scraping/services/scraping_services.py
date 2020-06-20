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
from financial.apps.scraping.models import NemotechModel

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

    def get_nemos(self, save=False):
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
        if save:
            self.save_nemos(result)
        return result

    def save_nemos(self, nemos):
        nemos_object = [
            NemotechModel(**nemo)
            for nemo in nemos
        ]
        NemotechModel.objects.bulk_create(nemos_object)
    
    def details_by_nemo(self):
        uris = props['uri']
        resume_price_url = uris['get_resumen_precios']


        headers = deepcopy(props['headers'])
        headers['X-CSRF-Token'] = self._get_csrf_token()
        response = self._session.post(
            url=f'{URL_BASE}{resume_price_url}',
            headers=headers,
            json={"nemo": "LTM"}, # Replace LTM with any nemo
            verify=False,
        )
        json_result = response.json()['listaResult']
        data_type = [result["tipo_dato"] for result in json_result] # List (data type)
        descriptions = [result["descripcion"] for result in json_result] # List descriptions
        import pdb; pdb.set_trace()