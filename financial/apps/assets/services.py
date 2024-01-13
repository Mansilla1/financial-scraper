import arrow
from typing import Dict, List, Optional, Union

from financial.apps.assets import providers
from financial.apps.assets.dataclasses import AssetData, AssetPriceData
from financial.apps.assets.exceptions import AssetDoesNotExist, AssetAlreadyExists
from financial.apps.utils.constants import PRICES_DATE_RANGE_FORMAT_STRING
from financial.apps.utils.dataclasses import build_dataclass_from_model_instance
from financial.apps.utils.dates import get_start_date_based_in_price_data_range_format_string


def get_assets_data() -> List[AssetData]:
    data = providers.get_assets()
    return [
        AssetData(
            uuid=asset.uuid,
            name=asset.name,
            ticker=asset.ticker,
            country=asset.country,
            currency=asset.currency,
            active=asset.active,
        )
        for asset in data
    ]


def get_asset_data_by_ticker(ticker: str) -> Optional[AssetData]:
    try:
        asset = providers.get_asset_by_ticker(ticker=ticker)
        return AssetData(
            uuid=asset.uuid,
            name=asset.name,
            ticker=asset.ticker,
            country=asset.country,
            currency=asset.currency,
            active=asset.active,
        )
    except AssetDoesNotExist:
        return None


def create_new_asset(asset_data: AssetData) -> AssetData:
    try:
        asset = providers.get_asset_by_ticker(ticker=asset_data.ticker)
        if asset:
            raise AssetAlreadyExists
    except AssetDoesNotExist:
        pass

    asset = providers.create_new_asset(asset_data=asset_data)
    return AssetData(
        uuid=asset.uuid,
        name=asset.name,
        ticker=asset.ticker,
        country=asset.country,
        currency=asset.currency,
        active=asset.active,
    )


def asset_prices_bulk_creation(asset_prices_data: List[AssetPriceData]) -> None:
    providers.asset_prices_bulk_creation(asset_prices_data=asset_prices_data)


def get_assets_prices_data_by_nemos(nemos: List[str], range_string: str, until_date: Optional[arrow.Arrow] = None) -> List[Dict[str, Union[str, List[AssetPriceData]]]]:
    range_string = PRICES_DATE_RANGE_FORMAT_STRING.get(range_string)
    if not range_string:
        raise ValueError("Invalid range string")

    end_date = until_date or arrow.now()
    start_date = get_start_date_based_in_price_data_range_format_string(range_string=range_string, end_date=end_date)

    data = providers.get_assets_prices_by_nemos_and_date_range(
        nemos=nemos,
        date_range=(start_date, end_date),
    )
    unique_assets = set([asset_price.asset.ticker for asset_price in data])
    result = []
    for asset in unique_assets:
        asset_prices = [asset_price for asset_price in data if asset_price.asset.ticker == asset]
        result.append({
            "nemo": asset,
            "historical_prices": [
                build_dataclass_from_model_instance(
                    klass=AssetPriceData,
                    instance=asset_price,
                    asset=build_dataclass_from_model_instance(klass=AssetData, instance=asset_price.asset),
                    asset_name=asset_price.asset.ticker,
                    asset_uuid=asset_price.asset.uuid,
                )
                for asset_price in asset_prices
            ]
        })

    return result
