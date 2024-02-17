import arrow
import argparse

from decimal import Decimal
from copy import deepcopy
from collections import OrderedDict
from typing import Dict, List, Optional

from services.firestore import FirestoreConnectionService
from services.iex_cloud import get_raw_iex_charts_batch_records
from services.utils import chunks
from services.web_scraping import YahooFinanceWebScraping


IEX_TOKEN = "pk_2902dc5689d44690951a1c60e52fc527"

CHART_OPTIONS = OrderedDict({
    "1D": "1d",
    "1M": "1m",
    "MTD": "1m",
    "YTD": "1y",
    "12M": "1y",
    "5Y": "5y",
})
# TZ_INFO = "America/New_York"
TZ_INFO_MAP = {
    "iex_cloud": "America/New_York",
    "yahoo_finance": "America/Santiago",
}
ORIGIN_MAP = {
    "iex_cloud": "iex_cloud",
    "iex": "iex_cloud",
    "yahoo": "yahoo_finance",
    "yahoo_finance": "yahoo_finance",
}

# TODO: do it for portfolio assets too


def get_params():
    parse = argparse.ArgumentParser()
    parse.add_argument("--assets", nargs="*", help="AssetsId to update")
    parse.add_argument("--env", nargs="*", help="Environment")
    parse.add_argument("--chart_type", nargs="*", help="chart type: 1D, 1M, 12M, MTD, YTD, 5Y")
    parse.add_argument("--origin", nargs="*", help="origin")
    args = parse.parse_args()
    return args


def get_assets_ids(
    assets_ids: List[str],
    firestore_service: FirestoreConnectionService,
) -> List[str]:
    assets = firestore_service.get_dw_assets()

    assets_dict = [doc.to_dict() for doc in assets]
    if assets_ids:
        assets_dict = list(filter(lambda x: x["assetId"] in assets_ids, assets_dict))
    return list(map(lambda x: x["assetId"], assets_dict))


def remove_duplicates_records(
    records: List[Dict[str, str]],
    key: str,
) -> List[Dict[str, str]]:
    aux_dict = {}
    result = []
    for record in records:
        if record[key] not in aux_dict:
            result.append(record)
            aux_dict[record[key]] = True

    return result


def get_graph_from_provider_data_by_chart_type(
    chart_type: str,
    provider_data: List[Dict[str, str]],
    previous_value: Optional[Decimal] = None,
    origin: str = "iex_cloud",
) -> List[Dict[str, str]]:
    if chart_type == "1D":
        new_graph = []
        last_value = previous_value

        for chart in provider_data:
            share_price = chart.get("close") or last_value
            if share_price:
                last_value = share_price

            new_graph.append({
                "date": arrow.get(f"{chart['date']}T{chart['minute']}", tzinfo=TZ_INFO_MAP[origin]).datetime,
                "sharePrice": share_price,
            })

        return new_graph

    last_chart_date = provider_data[-1]["date"]
    default_result = [
        {
            "date": arrow.get(
                f"{chart['date']}T{'16:00' if chart['date'] != last_chart_date else '01:00'}",
                tzinfo=TZ_INFO_MAP[origin],
            ).datetime,
            "sharePrice": chart["close"],
        }
        for chart in provider_data
        if chart.get("date") and chart.get("close")
    ]

    start_date = default_result[0]["date"] if default_result else None
    if chart_type == "MTD":
        start_date = arrow.get().replace(day=1).date()
    elif chart_type == "YTD":
        start_date = arrow.get().replace(month=1, day=1).date()

    if not start_date:
        return default_result

    return [
        chart
        for chart in default_result
        if arrow.get(chart["date"]) >= arrow.get(start_date)
    ]


def get_data_to_update_by_asset_id(
    data_from_provider: Dict[str, List[Dict[str, str]]],
    assets_periods_info: Dict[str, List[Dict[str, str]]],
    chart_type: str,
    origin: str = "iex_cloud",
) -> Dict[str, List[Dict[str, str]]]:
    print("Transforming data to update by assetId...")

    result = {}
    for asset_id, provider_data in data_from_provider.items():
        period_info = assets_periods_info.get(asset_id)
        if period_info is None or not period_info:
            print(f"No periods info for assetId: {asset_id}; skipping...")
            continue

        new_period_info = []
        for period in deepcopy(period_info):
            if period.get("period") != chart_type:
                new_period_info.append(period)
                continue

            previous_graph = period.get("graph", [])
            previous_value = None
            if previous_graph:
                previous_value = previous_graph[0].get("sharePrice")

            graph_from_iex = get_graph_from_provider_data_by_chart_type(
                chart_type=chart_type,
                provider_data=provider_data.get("chart"),
                previous_value=previous_value,
                origin=origin,
            )

            final_graph = graph_from_iex or previous_graph
            new_period_info.append({
                **period,
                "graph": final_graph,
                "comparePrice": final_graph[0]["sharePrice"] if final_graph else period.get("comparePrice"),
            })

        if chart_type not in [period.get("period") for period in new_period_info]:
            graph_from_iex = get_graph_from_provider_data_by_chart_type(
                chart_type=chart_type,
                provider_data=provider_data.get("chart"),
                previous_value=None,
                origin=origin,
            )
            new_period_info.append({
                "period": chart_type,
                "graph": sorted(graph_from_iex, key=lambda x: x["date"]),
                "comparePrice": graph_from_iex[0]["sharePrice"] if graph_from_iex else None,
            })

        result[asset_id] = sorted(new_period_info, key=lambda x: CHART_OPTIONS[x["period"]])

    return result


def get_assets_info(assets_ids: List[str], firestore_service: FirestoreConnectionService) -> Dict[str, Dict[str, str]]:
    result = {}
    for asset_id in assets_ids:
        asset = firestore_service.get_asset_by_id(asset_id=asset_id)
        result[asset_id] = asset.to_dict()

    return result


def get_assets_data_by_origin(
    assets_ids: List[str],
    origin: str,
    chart_type: str,
) -> Dict[str, List[Dict[str, str]]]:
    if origin == "iex_cloud":
        return get_raw_iex_charts_batch_records(
            assets_ids=assets_ids,
            token=IEX_TOKEN,
            time_range=CHART_OPTIONS[chart_type],
            time_sleep=0,
        )
    elif origin == "yahoo_finance":
        web_scraping_service = YahooFinanceWebScraping()
        data = {}
        for asset_id in assets_ids:
            data[asset_id] = {
                "chart": web_scraping_service.get_transformed_asset_prices_result(asset_id=asset_id, range_type=chart_type)
            }

        return data

    return {}


def update_charts(
    chart_type: str,
    assets_ids: Optional[List[str]] = None,
    env: str = "qa",
    origin: str = "iex_cloud",
) -> None:
    firestore_service = FirestoreConnectionService(environment=env)

    assets_ids = get_assets_ids(
        assets_ids=assets_ids,
        firestore_service=firestore_service,
    )
    assets_periods_info = firestore_service.get_assets_periods_info_by_assets_ids(assets_ids=assets_ids)

    data_from_provider = get_assets_data_by_origin(
        assets_ids=assets_ids,
        origin=origin,
        chart_type=chart_type,
    )

    data_to_update = get_data_to_update_by_asset_id(
        data_from_provider=data_from_provider,
        assets_periods_info=assets_periods_info,
        chart_type=chart_type,
        origin=origin,
    )

    data_to_update_keys_chunks = chunks(
        lst=list(data_to_update.keys()),
        chunk_size=100,
    )

    for data_to_update_keys in data_to_update_keys_chunks:
        data_to_update_ = {
            data_to_update_key: data_to_update[data_to_update_key]
            for data_to_update_key in data_to_update_keys
        }
        print(f"Updating {len(data_to_update_keys)} assets...")
        firestore_service.update_assets_periods_info_by_assets_ids(data_to_update=data_to_update_)


if __name__ == "__main__":
    # execution example: python update_charts.py --assets AAPL --env qa --chart_type 1d
    args = get_params()

    if not IEX_TOKEN:
        raise ValueError("IEX_TOKEN is required!")

    env = args.env[0] if ("env" in args and args.env) else "qa"
    print(f"Executing in {env} env...")

    assets = args.assets if "assets" in args else None
    chart_type = args.chart_type[0] if ("chart_type" in args and args.chart_type) else None
    if not chart_type:
        raise ValueError("Chart type is required!")

    chart_type = chart_type.strip().upper()

    if not assets:
        raise ValueError("Assets is required!")

    if chart_type not in CHART_OPTIONS.keys():
        raise ValueError(f"Invalid chart type: {chart_type}")

    origin = (args.origin[0] if ("origin" in args and args.origin) else 'iex_cloud').lower()
    origin = ORIGIN_MAP.get(origin)
    if not origin:
        raise ValueError(f"Invalid origin: {origin} or dont add it")

    update_charts(
        chart_type=chart_type,
        assets_ids=assets,
        env=env,
        origin=origin,
    )

    print("Done!")
