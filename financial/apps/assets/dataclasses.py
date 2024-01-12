import arrow

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class AssetData:
    name: str
    ticker: str
    uuid: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    active: Optional[bool] = True
    created_at: Optional[Union[arrow.Arrow, str]] = None
    updated_at: Optional[Union[arrow.Arrow, str]] = None

    def serialize(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "ticker": self.ticker,
            "description": self.description,
            "currency": self.currency,
            "country": self.country,
            "active": self.active,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }


@dataclass
class AssetPriceData:
    asset: AssetData
    close: Optional[float] = None
    adj_close: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    volume: Optional[int] = None
    date: Optional[Union[arrow.Arrow, str]] = None
    time: Optional[Union[arrow.Arrow, str]] = None
    created_at: Optional[Union[arrow.Arrow, str]] = None
    updated_at: Optional[Union[arrow.Arrow, str]] = None

    def serialize(self):
        return {
            "asset": self.asset.serialize(),
            "close": self.close,
            "adj_close": self.adj_close,
            "high": self.high,
            "low": self.low,
            "open": self.open,
            "volume": self.volume,
            "date": str(self.date) if self.date else None,
            "time": str(self.time) if self.time else None,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
