import arrow

from financial.apps.utils.constants import PRICES_DATE_RANGE_FORMAT_STRING
from financial.apps.utils.exceptions import InvalidRangeString


def get_start_date_based_in_price_data_range_format_string(range_string: str, end_date: arrow.Arrow) -> arrow.Arrow:
    range_string = PRICES_DATE_RANGE_FORMAT_STRING.get(range_string)
    if not range_string:
        raise InvalidRangeString

    if range_string == "1d":
        return end_date.shift(days=-1)
    elif range_string == "5d":
        return end_date.shift(days=-5)
    elif range_string == "1m":
        return end_date.shift(months=-1)
    elif range_string == "3m":
        return end_date.shift(months=-3)
    elif range_string == "6m":
        return end_date.shift(months=-6)
    elif range_string == "1y":
        return end_date.shift(years=-1)
    elif range_string == "2y":
        return end_date.shift(years=-2)
    elif range_string == "5y":
        return end_date.shift(years=-5)
    elif range_string == "10y":
        return end_date.shift(years=-10)
    elif range_string == "ytd":
        return end_date.shift(years=-1).replace(month=12, day=31).shift(days=1)
    elif range_string == "mtd":
        return end_date.replace(day=1)
    elif range_string == "max":
        return end_date.shift(years=-15)
    else:
        raise InvalidRangeString
