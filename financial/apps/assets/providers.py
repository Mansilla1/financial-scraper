import arrow

from typing import List, Tuple

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
            asset_id=asset_price_data.asset.uuid,
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


def get_assets_prices_by_nemos_and_date_range(nemos: List[str], date_range: Tuple[arrow.Arrow, arrow.Arrow]) -> List[AssetPrice]:
    return AssetPrice.objects.select_related("asset").filter(
        asset__ticker__in=nemos,
        date__gte=date_range[0].date(),
        date__lte=date_range[1].date(),
    )
