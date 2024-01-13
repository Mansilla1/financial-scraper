from typing import List

from financial.apps.geo.models import Country
from financial.apps.geo.exceptions import GeoDoesNotExist, NotActiveGeoException


def get_active_countries() -> List[Country]:
    return Country.objects.filter(status=True)


def get_country_by_iso2_code(iso2_code: str) -> Country:
    try:
        country = Country.objects.get(iso2_code=iso2_code)
        if not country.status:
            raise NotActiveGeoException
        return country
    except Country.DoesNotExist:
        raise GeoDoesNotExist
