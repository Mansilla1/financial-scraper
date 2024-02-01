import requests
import time

from typing import List, Dict, Optional

from .utils import chunks


IEX_URL = 'https://cloud.iexapis.com/stable'
CHUNKS_SIZE = 100
IEX_DEFAULT_RANGE_PERIOD = "1m"


def get_raw_iex_charts_batch_records(
    assets_ids: List[str],
    token: str,
    time_range: Optional[str] = None,
    time_sleep: Optional[int] = None,
) -> Dict[str, List[Dict[str, str]]]:
    time_range = time_range or IEX_DEFAULT_RANGE_PERIOD
    print(f"Getting IEX records for range: {time_range}...")

    chunks_list = chunks(lst=assets_ids, chunk_size=CHUNKS_SIZE)
    result = {}
    for assets in chunks_list:
        symbols = ",".join(assets)
        query_params = {
            "token": token,
            "symbols": symbols,
            "types": "chart",
            "range": time_range,
        }
        records = requests.get(f"{IEX_URL}/stock/market/batch", params=query_params)
        result.update(records.json())
        if time_sleep:
            print(f"Sleeping {time_sleep} seconds...")
            time.sleep(time_sleep)

    print(f"{len(result.keys())} records retrieved from IEX API")
    return result


def get_iex_charts_batch_records(
    assets_ids: List[str],
    token: str,
    time_range: Optional[str] = None,
    time_sleep: Optional[int] = None,
) -> Dict[str, List[Dict[str, str]]]:
    result = get_raw_iex_charts_batch_records(
        assets_ids=assets_ids,
        token=token,
        time_range=time_range,
        time_sleep=time_sleep,
    )
    return {
        asset_id: [
            {"date": chart["date"], "sharePrice": chart["close"]}
            for chart in asset_records["chart"]
        ]
        for asset_id, asset_records in result.items()
    }
