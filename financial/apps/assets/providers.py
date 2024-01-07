from typing import List

from financial.apps.assets.exceptions import AssetDoesNotExist
from financial.apps.assets.models import Asset


def get_assets() -> List[Asset]:
    return Asset.objects.all()


def get_asset_by_ticker(ticker: str) -> Asset:
    try:
        return Asset.objects.get(ticker=ticker)
    except Asset.DoesNotExist:
        raise AssetDoesNotExist


def create_new_asset(asset_data: Asset) -> Asset:
    return Asset.objects.create(
        name=asset_data.name,
        ticker=asset_data.ticker,
        description=asset_data.description,
        currency=asset_data.currency,
        country=asset_data.country,
    )
