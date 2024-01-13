from typing import List, Optional

from financial.apps.geo.dataclasses import CountryData
from financial.apps.geo.exceptions import GeoDoesNotExist, NotActiveGeoException
from financial.apps.geo.providers import get_country_by_iso2_code, get_active_countries


def get_country_data_by_iso2_code(iso2_code: str) -> Optional[CountryData]:
    try:
        country = get_country_by_iso2_code(iso2_code=iso2_code)
        return CountryData(
            uuid=country.uuid,
            name=country.name,
            iso2_code=country.iso2_code,
            iso3_code=country.iso3_code,
            languaje=country.languaje,
            currency=country.currency,
            currency_symbol=country.currency_symbol,
            currency_decimal_sep=country.currency_decimal_sep,
            currency_thousands_sep=country.currency_thousands_sep,
            timezone=country.timezone,
            status=country.status,
        )
    except (NotActiveGeoException, GeoDoesNotExist):
        raise GeoDoesNotExist


def get_active_country_data() -> List[CountryData]:
    data = get_active_countries()
    return [
        CountryData(
            uuid=country.uuid,
            name=country.name,
            iso2_code=country.iso2_code,
            iso3_code=country.iso3_code,
            languaje=country.languaje,
            currency=country.currency,
            currency_symbol=country.currency_symbol,
            currency_decimal_sep=country.currency_decimal_sep,
            currency_thousands_sep=country.currency_thousands_sep,
            timezone=country.timezone,
            status=country.status,
        )
        for country in data
    ]
