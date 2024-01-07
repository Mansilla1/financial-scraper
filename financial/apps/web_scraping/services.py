import requests

from copy import deepcopy
from json.decoder import JSONDecodeError
from typing import List

from financial.apps.assets import dataclasses as assets_dataclasses
from financial.apps.assets import services as assets_services
from financial.apps.web_scraping.exceptions import (
    InvalidCSRFToken,
    InvalidResponse,
)
from financial.apps.web_scraping.dataclasses import GetNemoPriceResponseData


class BolsaDeSantiagoWebScraping:
    _URL_BASE = "https://www.bolsadesantiago.com"
    _ENDPOINT = {
        "csrf": "/api/Securities/csrfToken",
        "get_prices_nemos": "/api/RV_ResumenMercado/getAccionesPrecios",
    }
    _HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        # "Content-Length": "2",
        "Content-Type": "application/json;charset=UTF-8",
        # "Cookie": "BCS-HTML5_corporativa-443-PROD=684715681.20480.0000; gb-wbchtbt-uid=1591892299902; _csrf=GjqJBqBp8g2utqY0YXHvFOYc; _ga=GA1.2.2090315841.1591892304; _gid=GA1.2.1663141191.1591892304; __gads=ID=da6dac373caf459c:T=1591892304:S=ALNI_MbLcJ6pcWmMhI61KvNMEF1unZ-CmA; _gat=1",
        "DNT": "1",
        "Host": "www.bolsadesantiago.com",
        "Origin": _URL_BASE,
        "Referer": f"{_URL_BASE}/acciones_precios",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        # "X-CSRF-Token": "lzN0ykSE-zU-dYStFUocaGAp-KbeF3HtzndQ",
    }

    def __init__(self):
        self._session = requests.Session()

    def _get_csrf_token(self) -> str:
        csrf_url = f"{self._URL_BASE}{self._ENDPOINT['csrf']}"
        try:
            csrf_response = self._session.get(
                url=csrf_url,
                verify=True,
            )

            if not csrf_response.ok:
                raise InvalidCSRFToken

            csrf_token = (csrf_response.json() or {}).get("csrf")
            if not csrf_token:
                raise InvalidCSRFToken

        except (JSONDecodeError, KeyError):
            raise InvalidCSRFToken

        return csrf_token

    def get_nemos_price_data(self) -> List[GetNemoPriceResponseData]:
        url = f"{self._URL_BASE}{self._ENDPOINT['get_prices_nemos']}"

        headers = deepcopy(self._HEADERS)
        headers["X-CSRF-Token"] = self._get_csrf_token()

        response = self._session.post(
            url=url,
            headers=headers,
            json={},
            verify=True,
        )

        if not response.ok:
            raise InvalidResponse

        try:
            json_result = response.json()["listaResult"]

            nemo_data_list = [
                GetNemoPriceResponseData(
                    green_bonus=response.get("BONO_VERDE"),
                    djsi=response.get("DJSI"),
                    etfs_foreign=response.get("ETFs_EXTRANJERO"),
                    isin=response.get("ISIN"),
                    coin=response.get("MONEDA"),
                    amount=response.get("MONTO"),
                    nemo=response.get("NEMO"),
                    weight=response.get("PESO"),
                    close_price=response.get("PRECIO_CIERRE"),
                    buy_price=response.get("PRECIO_COMPRA"),
                    sell_price=response.get("PRECIO_VENTA"),
                    traded_units=response.get("UN_TRANSADAS"),
                    variant=response.get("VARIACION"),
                )
                for response in json_result
            ]
        except (JSONDecodeError, KeyError):
            return []

        return nemo_data_list

    def save_nemos(self, nemos_price_data: List[GetNemoPriceResponseData]) -> None:
        for asset_data in nemos_price_data:
            try:
                asset_data = assets_dataclasses.AssetData(
                    name=asset_data.nemo,
                    ticker=asset_data.nemo,
                    currency="CLP",
                )
                assets_services.create_new_asset(asset_data=asset_data)
            except Exception as e:
                # import pdb; pdb.set_trace()
                pass
