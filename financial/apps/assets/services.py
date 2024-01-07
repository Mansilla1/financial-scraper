from typing import List, Optional

from financial.apps.assets.dataclasses import AssetData
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
