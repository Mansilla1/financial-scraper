from typing import List, Optional

from financial.apps.assets.dataclasses import AssetData, AssetPriceData
from financial.apps.assets.exceptions import AssetDoesNotExist, AssetAlreadyExists
from financial.apps.assets import providers


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
    return None


def get_assets_prices_data_by_assets_ids(assets_ids: List[str]) -> List[AssetPriceData]:
    data = providers.get_assets_prices_by_ids(assets_ids=assets_ids)
    unique_assets = set([asset_price.asset for asset_price in data])
    result = []
    for asset in unique_assets:
        asset_data = get_asset_data_by_ticker(ticker=asset)
        asset_prices = [asset_price for asset_price in data if asset_price.asset == asset]
        result.append(
            AssetPriceData(
                asset=asset_data,
                close=asset_prices[-1].close,
                adj_close=asset_prices[-1].adj_close,
                high=asset_prices[-1].high,
                low=asset_prices[-1].low,
                open=asset_prices[-1].open,
                volume=asset_prices[-1].volume,
                date=asset_prices[-1].date,
                time=asset_prices[-1].time,
            )
        )

    return result
