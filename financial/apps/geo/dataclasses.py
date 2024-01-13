import uuid

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class CountryData:
    uuid: Union[uuid.UUID, str]
    name: str
    iso2_code: str
    iso3_code: Optional[str] = None
    languaje: Optional[str] = None
    currency: Optional[str] = None
    currency_symbol: Optional[str] = None
    currency_decimal_sep: Optional[str] = None
    currency_thousands_sep: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[bool] = None

    def serialize(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "iso2_code": self.iso2_code,
            "iso3_code": self.iso3_code,
            "languaje": self.languaje,
            "currency": self.currency,
            "currency_symbol": self.currency_symbol,
            "currency_decimal_sep": self.currency_decimal_sep,
            "currency_thousands_sep": self.currency_thousands_sep,
            "timezone": self.timezone,
            "status": self.status,
        }
