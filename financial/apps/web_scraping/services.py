import arrow
import logging
import requests

from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Union

from financial.apps.assets import dataclasses as assets_dataclasses
from financial.apps.assets import services as assets_services
from financial.apps.web_scraping.exceptions import (
    InvalidCSRFToken,
    InvalidResponse,
)
from financial.apps.web_scraping.dataclasses import GetNemoPriceResponseData, HistoricalNemoPriceResponseData, ResultMapDataForNemoData


logger = logging.getLogger(__name__)


class WebScrapingService(ABC):
    _URL_BASE = None
    _HEADERS = None
    _ENDPOINTS = None

    def __init__(self, *args, **kwargs):
        self._session = requests.Session()

    @abstractmethod
    def get_nemos_price_data(self, nemos: Optional[List[str]] = None) -> List[GetNemoPriceResponseData]:
        raise NotImplementedError

    @abstractmethod
    def get_historical_prices_by_nemo(self, nemo: str) -> List[HistoricalNemoPriceResponseData]:
        raise NotImplementedError

    @abstractmethod
    def save_nemos(self, nemos_price_data: List[GetNemoPriceResponseData]) -> None:
        pass

    @abstractmethod
    def save_nemos_historical_prices(self, nemos_price_data: Dict[str, List[HistoricalNemoPriceResponseData]]) -> None:
        pass


class BolsaDeSantiagoWebScraping(WebScrapingService):
    _URL_BASE = "https://www.bolsadesantiago.com"
    _ENDPOINTS = {
        "csrf": "/api/Securities/csrfToken",
        "get_prices_nemos": "/api/RV_ResumenMercado/getAccionesPrecios",
        "get_historical_prices": "/api/RV_Instrumentos/getPointHistGAT",
        "get_dividends": "/api/RV_ResumenMercado/getDividendos",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._token = None

    def _get_csrf_token(self) -> str:
        csrf_url = f"{self._URL_BASE}{self._ENDPOINTS['csrf']}"
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

    def set_csrf_token(self) -> None:
        self._token = self._get_csrf_token()

    def get_nemos_price_data(self, nemos: Optional[List[str]] = None) -> List[GetNemoPriceResponseData]:
        url = f"{self._URL_BASE}{self._ENDPOINTS['get_prices_nemos']}"

        headers = deepcopy(self._HEADERS)
        if not self._token:
            self.set_csrf_token()

        headers["X-CSRF-Token"] = self._token

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
            if nemos:
                json_result = filter(lambda x: x.get("NEMO") in nemos, json_result)

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

    def get_historical_prices_by_nemo(self, nemo: str) -> List[HistoricalNemoPriceResponseData]:
        url = f"{self._URL_BASE}{self._ENDPOINTS['get_historical_prices']}"

        headers = deepcopy(self._HEADERS)
        if not self._token:
            self.set_csrf_token()

        headers["X-CSRF-Token"] = self._token

        try:
            response = self._session.get(
                url=url,
                headers=headers,
                params={"nemo": nemo},
                verify=True,
            )
            if not response.ok:
                raise InvalidResponse

            json_result = response.json().get("listaResult")
            if not json_result:
                return []

            historical_prices = [
                HistoricalNemoPriceResponseData(
                    adj_close=response.get("ADJ_CLOSE"),
                    close=response.get("CLOSE"),
                    date=response.get("DATE"),
                    high=response.get("HIGH"),
                    low=response.get("LOW"),
                    open=response.get("OPEN"),
                    volume=response.get("VOLUME"),
                )
                for response in json_result
            ]
            return historical_prices
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout error {e}")
            return []

    def get_dividends(self, nemo: str, from_date: arrow.Arrow, to_date: arrow.Arrow) -> List[Dict[str, Any]]:
        url = f"{self._URL_BASE}{self._ENDPOINTS['get_dividends']}"
        headers = deepcopy(self._HEADERS)
        if not self._token:
            self.set_csrf_token()

        headers["X-CSRF-Token"] = self._token
        try:
            response = self._session.post(
                url=url,
                headers=headers,
                json={
                    "nemo": nemo,
                    "fechaDesde": from_date.strftime("%Y-%m-%d"),
                    "fechaHasta": to_date.strftime("%Y-%m-%d"),
                },
                verify=True,
            )
            if not response.ok:
                raise InvalidResponse

            json_result = response.json().get("listaResult")
            if not json_result:
                return []

            return json_result
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout error {e}")
            return []

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
                logger.error(e)

    def save_nemos_historical_prices(self, nemos_price_data: Dict[str, List[HistoricalNemoPriceResponseData]]) -> None:
        for nemo, prices_data in nemos_price_data.items():
            asset_data = assets_services.get_asset_data_by_ticker(ticker=nemo)
            if not asset_data:
                self.save_nemos(nemos_price_data=[nemo])
                asset_data = assets_services.get_asset_data_by_ticker(ticker=nemo)

            if not asset_data:
                continue
            try:
                assets_price_data = [
                    assets_dataclasses.AssetPriceData(
                        asset=asset_data,
                        adj_close=price_data.adj_close,
                        close=price_data.close,
                        date=price_data.date,
                        high=price_data.high,
                    )
                    for price_data in prices_data
                ]
                assets_services.asset_prices_bulk_creation(asset_prices_data=assets_price_data)
            except Exception as e:
                logger.error(e)


class YahooFinanceWebScraping(WebScrapingService):
    _URL_BASE = "https://query1.finance.yahoo.com/"
    _ENDPOINTS = {
        "asset_info": "v8/finance/chart/{asset_id}?region=US&lang=en-US&includePrePost=false&interval={interval}&useYfid=true&range={range_type}&corsDomain=finance.yahoo.com&.tsrc=finance",
    }
    _HEADERS = {
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        # 'Referer': 'https://finance.yahoo.com/quote/VYMI/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"'
    }

    _INTERVALS = {
        "1d": "1m",
    }
    _RANGE_TYPE = {
        "1d": "1d",
        "1m": "1mo",
        "mtd": "1mo",
        "1y": "1y",
        "ytd": "1y",
        "5y": "5y",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result_map: List[ResultMapDataForNemoData] = []

    def get_nemos_price_data(self, nemos: Optional[List[str]] = None) -> List[GetNemoPriceResponseData]:
        if not nemos:
            logging.info("No nemos provided")
            return []

        range_type = "1d"
        nemos_data = []
        for nemo in nemos:
            nemo_data = next(filter(lambda x, y=nemo, z=range_type: x.nemo == y and x.range == z, self._result_map), None)
            if not nemo_data:
                nemo_data_list = self._get_scraped_data_by_nemo(nemo=nemo, range_type=range_type)
            else:
                nemo_data_list = nemo_data.data
            nemos_data.extend(nemo_data_list)

        return nemos_data

    def get_historical_prices_by_nemo(self, nemo: str) -> List[HistoricalNemoPriceResponseData]:
        range_type = "5y"
        nemo_data = next(filter(lambda x, y=nemo, z=range_type: x.nemo == y and x.range == z, self._result_map), None)
        if not nemo_data:
            return self._get_scraped_data_by_nemo(nemo=nemo, range_type=range_type)

        return nemo_data.data

    def _get_scraped_data_by_nemo(self, nemo: str, range_type: str) -> List[Union[HistoricalNemoPriceResponseData, GetNemoPriceResponseData]]:
        range_type = range_type.lower()
        interval = self._INTERVALS.get(range_type, "1d")
        url = f"{self._base_url}{self._ENDPOINTS['asset_info'].format(asset_id=nemo, interval=interval, range_type=self._RANGE_TYPE[range_type])}"
        headers = deepcopy(self.headers)
        headers["Referer"] = f"https://finance.yahoo.com/quote/{nemo}/"
        response = self._session.get(url=url, headers=headers, verify=True)
        if not response.ok:
            return []

        response_json = response.json()
        if not response_json:
            return []

        result = response_json.get("chart", {}).get("result", [])
        if not result:
            return []

        transformed_result = self._get_transformed_result(result=result[0], nemo=nemo, range_type=range_type)
        result_data_ = ResultMapDataForNemoData(
            nemo=nemo,
            range=range_type,
            data=transformed_result,
        )
        self._result_map.append(result_data_)
        return transformed_result

    def _get_transformed_result(self, result: List[Any], nemo: str, range_type: str) -> List[Union[HistoricalNemoPriceResponseData, GetNemoPriceResponseData]]:
        timestamp = result.get("timestamp", [])
        timestamps = [datetime.fromtimestamp(ts) for ts in timestamp]
        indicators = result.get("indicators", {}).get("quote", [{}])[0] or {}
        result = []
        for i in range(len(timestamps)):
            open_price = indicators.get("open", [])[i]
            close_price = indicators.get("close", [])[i]
            high_price = indicators.get("high", [])[i]
            low_price = indicators.get("low", [])[i]
            volume = indicators.get("volume", [])[i]

            if range_type == "1d":
                result.append(
                    GetNemoPriceResponseData(
                        green_bonus=None,
                        djsi=None,
                        etfs_foreign=None,
                        isin=None,
                        coin=None,
                        amount=None,
                        nemo=nemo,
                        weight=None,
                        close_price=close_price,
                        buy_price=None,
                        sell_price=None,
                        traded_units=None,
                        variant=None,
                        minute=timestamps[i].strftime("%H:%M"),
                    ),
                )
            else:
                result.append(
                    HistoricalNemoPriceResponseData(
                        adj_close=None,
                        close=close_price,
                        date=timestamps[i].strftime("%Y-%m-%d"),
                        high=high_price,
                        low=low_price,
                        open=open_price,
                        volume=volume,
                    ),
                )

        return result
