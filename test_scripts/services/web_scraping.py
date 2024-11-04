import arrow
import requests

from bs4 import BeautifulSoup
from copy import deepcopy
from datetime import datetime
from typing import Tuple, List, Dict, Any


class BolsaDeSantiagoWebScraping:
    _ENDPOINTS = {
        "csrf_token": "/api/Securities/csrfToken",
        "dividends": "/api/RV_ResumenMercado/getDividendos",
    }
    headers = {
        "csrf_token": {
            "authority": "www.bolsadesantiago.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.7",
            # "authorization": "u3OAjlfEsAlGL4gURnoGFHhwENDoB1xOwWKVXXNmbWgikgX1fKZZ37pdWU4OFF85",
            "if-none-match": 'W/"2f-HAA5e05R8LwN7I5wo0fmlIFGi4U"',
            "referer": "https://www.bolsadesantiago.com/resumen_instrumento/IVVCL",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # "Cookie": "f5avraaaaaaaaaaaaaaaa_session_=ALPMDOPMLNJHBICKNJFPAPPBHMBNGEOMGFAJKIGHKHACAFKCNDHLDBJHJOPPDDGLJMCDMPIHLOFIIALFALBAKBMCMPGCGOIGGIJAAAHLHHNHNHCMBILFKFMDDLCGOJEK; BIGipServerPool-Push_HTML5_corporativa=684715681.20480.0000; BIGipServerPool-www.bolsadesantiago.com-HTML5_corporativa=684715681.20480.0000; __uzma=dae327f5-d0d0-4e33-981f-59c11a4c9b62; __uzmb=1704393025; __uzmc=7368872133603; __uzmd=1704722332; __uzme=8911; _csrf=6HBJ5VSiIL8D9VTvRph3_DMb"
        },
        "dividends": {
            "authority": "www.bolsadesantiago.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.7",
            "authorization": "u3OAjlfEsAlGL4gURnoGFHhwENDoB1xOwWKVXXNmbWgikgX1fKZZ37pdWU4OFF85",
            "content-type": "application/json;charset=UTF-8",
            # "cookie": "f5avraaaaaaaaaaaaaaaa_session_=EDPJJLLCOPJNJKPGFOIANPMBFEGKDFINGAJDOABGBCIOCGGMFGMELIMPANIIEJPBCJODOKDMIHPHJAOJKDMACLKINPKCCDINJBAHBBNCEFAGLHAJCOAOGMNGJGPNPOGB; __uzma=1b746b26-c06e-4a51-b90d-a8ea595a9ff6; __uzmb=1691416763; __uzme=1311; BIGipCookie=000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000; BIGipServerPool-Push_HTML5_corporativa=684715681.20480.0000; f5avraaaaaaaaaaaaaaaa_session_=IIBAPCLCFAOFAILLOCEEEBLCJFLFMOBIIOIOCCCJHIDJCIEFAKAAMPEFLCBAKFIFDHGDHIFMPICNNEEAKJJAKPNDGPEGJFEOLMCNOEHFMKPOCDJCFJJBINHEPIEJONMJ; _csrf=usiicZY9720bzoLneu84Xb2V; gb-wbchtbt-uid=1704314737087; _oauth2_proxy_csrf=DPTixsIJpUIR_NC7gak-apQmULRJuDEZIBJSWrYEpyyRYyuGQVwg4A1lWjkWyKxawVQ2NYRpVm--NK5uwV3oxKvalYPpSpT8hc_Nkbt9hiypd5uVTCuzGXI=|1704392729|3Q5H09em2wrC5POvXAvubQWmLN-udJxz9VFaISkGzR4=; BIGipServerPool-www.bolsadesantiago.com-HTML5_corporativa=701492897.20480.0000; __uzmc=7199171290684; __uzmd=1704392741; f5avraaaaaaaaaaaaaaaa_session_=PEJDLCIKNGACOIHCFCIDFJFOOCJGBANKGMAJCAPIEOHHPCELNIGMGDGJIEJGLBMKNAEDMFGJCAHPHBAAJEPANIMMPALKDAPFPNOBNOJBMAJLCNEEIMPPPGIILCOHDKDJ; BIGipServerPool-Push_HTML5_corporativa=684715681.20480.0000; BIGipServerPool-www.bolsadesantiago.com-HTML5_corporativa=718270113.20480.0000; __uzma=dae327f5-d0d0-4e33-981f-59c11a4c9b62; __uzmb=1704393025; __uzmc=9631171510562; __uzmd=1704722750; __uzme=8911; _csrf=6HBJ5VSiIL8D9VTvRph3_DMb",
            "origin": "https://www.bolsadesantiago.com",
            "referer": "https://www.bolsadesantiago.com/resumen_instrumento/IVVCL",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # "x-csrf-token": "wN4EGf3R-aFylV8_fKho7ybEnoJ4UJp2WATw"
        },
    }

    def __init__(self):
        self._base_url = "https://www.bolsadesantiago.com"
        self._session = requests.Session()
        self._csrf_token = None

    def get_csrf_token(self) -> str:
        if self._csrf_token:
            return self._csrf_token

        url = f"{self._base_url}{self._ENDPOINTS['csrf_token']}"
        response = self._session.get(url=url, headers=self.headers["csrf_token"], verify=True)
        csrf_token = response.json().get("csrf", "")
        self._csrf_token = csrf_token
        return csrf_token

    def _get_dividends_response_in_date_range(self, response_data: List[Dict[str, str]], dividends_date_range: Tuple[str, str]):
        result_records = response_data.get("listaResult") or []
        start_date = arrow.get(dividends_date_range[0]).date()
        end_date = arrow.get(dividends_date_range[1]).date()

        return [
            record
            for record in result_records
            if (
                "divid" in record.get("descrip_vc", "").lower()
                and start_date <= arrow.get(record.get("fec_pago")).date() <= end_date
            )
        ]

    def get_dividends_data_by_asset(self, asset_id: str, dividends_date_range: Tuple[str, str]):
        url = f"{self._base_url}{self._ENDPOINTS['dividends']}"
        headers = deepcopy(self.headers["dividends"])
        headers["X-CSRF-Token"] = self.get_csrf_token()

        data = {
            "nemo": asset_id,
            # "tamanopag": 0,
            # "pagina": 0,
        }
        response = self._session.post(url=url, headers=headers, json=data, verify=True)
        response_result = response.json()
        if not response_result:
            return []

        return self._get_dividends_response_in_date_range(response_data=response_result, dividends_date_range=dividends_date_range)


class SIIWebScraping:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    _ENDPOINTS = {
        "dolar": "valores_y_fechas/dolar/dolar{year}.htm",
    }

    def __init__(self):
        self._url = "https://www.sii.cl/"

    def get_table_records_from_html(self, html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, 'html.parser')
        result = {}

        for month_block in soup.find_all('div', class_='meses'):
            h3_tag = month_block.find('h3')
            if not h3_tag:
                continue
            month = h3_tag.text.strip()

            table = month_block.find('table')
            if not table:
                continue

            result[month] = []

            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                values = [cell.text.strip() for cell in cells]
                result[month].append(values)

        return result

    def _convert_data_to_list(self, data: Dict[str, Any], year: int) -> List[Dict[str, Any]]:
        result_list = []

        month_mapping = {
            'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
            'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
            'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12',
        }

        for month_name, rows in data.items():
            month = month_mapping[month_name]

            for row in rows:
                if len(row) >= 2:
                    day = row[0].zfill(2)
                    price = row[1].replace(',', '.')

                    try:
                        price = float(price)
                        date = f"{year}-{month}-{day}"
                        result_list.append({"date": date, "price": price})
                    except ValueError:
                        continue

        return sorted(result_list, key=lambda x: arrow.get(x["date"]).datetime)

    def _find_closest_date(self, date_str: str, data: List[Dict[str, Any]]):
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        closest_date = None
        min_diff = float('inf')

        for item in data:
            current_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
            diff = abs((current_date - input_date).days)

            if diff < min_diff:
                min_diff = diff
                closest_date = current_date

        return closest_date.strftime("%Y-%m-%d") if closest_date else None

    def get_dolar_value_by_month(self, iso_date: str) -> float:
        arrow_date = arrow.get(iso_date)
        year = arrow_date.year

        url = f"{self._url}{self._ENDPOINTS['dolar'].format(year=year)}"
        response = requests.get(url=url, headers=self.headers, verify=True)
        if not response.ok:
            return 0

        table_records = self.get_table_records_from_html(html=response.text)
        if not table_records:
            return 0

        format_records = self._convert_data_to_list(data=table_records, year=year)
        near_date = self._find_closest_date(date_str=iso_date, data=format_records)
        if not near_date:
            return 0

        price = next(filter(lambda x: x["date"] == near_date, format_records), {}).get("price", 0)
        print(f"Dolar for Date: {near_date}, Price: {price}")

        return float(price)


class YahooFinanceWebScraping:
    headers = {
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        # 'Referer': 'https://finance.yahoo.com/quote/VYMI/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"'
    }
    _ENDPOINTS = {
        "asset_info": "v8/finance/chart/{asset_id}?region=US&lang=en-US&includePrePost=false&interval={interval}&useYfid=true&range={range_type}&corsDomain=finance.yahoo.com&.tsrc=finance",
    }
    _RESULT_MAP = {}
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

    def __init__(self):
        self._base_url = "https://query1.finance.yahoo.com/"
        self._session = requests.Session()

    def get_asset_prices(self, asset_id: str, range_type: str):
        range_type = range_type.lower()
        interval = self._INTERVALS.get(range_type, "1d")
        url = f"{self._base_url}{self._ENDPOINTS['asset_info'].format(asset_id=asset_id, interval=interval, range_type=self._RANGE_TYPE[range_type])}"
        headers = deepcopy(self.headers)
        headers["Referer"] = f"https://finance.yahoo.com/quote/{asset_id}/"
        response = self._session.get(url=url, headers=headers, verify=True)
        if not response.ok:
            return {}

        response_json = response.json()
        if not response_json:
            return {}

        result = response_json.get("chart", {}).get("result", [])
        if not result:
            return {}

        self._RESULT_MAP[asset_id] = result[0]
        return self._RESULT_MAP[asset_id]

    def get_transformed_asset_prices_result(self, asset_id: str, range_type: str) -> List[Dict[str, str]]:
        result = self._RESULT_MAP.get(asset_id)
        if not result:
            result = self.get_asset_prices(asset_id=asset_id, range_type=range_type)

        # meta = result.get("meta", {})
        timestamp = result.get("timestamp", [])
        timestamps = [datetime.fromtimestamp(ts) for ts in timestamp]
        indicators = result.get("indicators", {}).get("quote", [{}])[0] or {}
        chart = []
        for i in range(len(timestamps)):
            open_price = indicators.get("open", [])[i]
            close_price = indicators.get("close", [])[i]
            high_price = indicators.get("high", [])[i]
            low_price = indicators.get("low", [])[i]
            volume = indicators.get("volume", [])[i]
            chart.append({
                "date": timestamps[i].strftime("%Y-%m-%d"),
                "minute": timestamps[i].strftime("%H:%M"),
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": volume,
            })

        return chart

