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
