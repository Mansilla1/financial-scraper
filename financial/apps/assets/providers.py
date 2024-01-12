from typing import List

from financial.apps.assets.exceptions import AssetDoesNotExist
from financial.apps.assets.models import Asset, AssetPrice


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


def asset_prices_bulk_creation(asset_prices_data: List[AssetPrice]) -> None:
    asset_prices = [
        AssetPrice(
            asset=asset_price_data.asset,
            close=asset_price_data.close,
            adj_close=asset_price_data.adj_close,
            high=asset_price_data.high,
            low=asset_price_data.low,
            open=asset_price_data.open,
            volume=asset_price_data.volume,
            date=asset_price_data.date,
            time=asset_price_data.time,
        )
        for asset_price_data in asset_prices_data
    ]
    AssetPrice.objects.bulk_create(asset_prices)


def get_assets_prices_by_ids(assets_ids: List[str]) -> List[AssetPrice]:
    return AssetPrice.objects.filter(asset_id__in=assets_ids)
