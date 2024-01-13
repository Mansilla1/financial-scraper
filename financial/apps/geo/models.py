from django.db import models

from financial.apps.utils.models import UUIDBaseModel


class Country(UUIDBaseModel):
    name = models.CharField(max_length=70, blank=False, null=False)
    iso2_code = models.CharField(max_length=2, blank=False, null=False)
    iso3_code = models.CharField(max_length=2, blank=True, null=True)
    languaje = models.CharField(max_length=5, blank=True, null=True)

    currency = models.CharField(max_length=3, blank=True, null=True)
    currency_symbol = models.CharField(max_length=5, null=True, blank=True)
    currency_decimal_sep = models.CharField(max_length=1, null=True, blank=True)
    currency_thousands_sep = models.CharField(max_length=1, blank=True, null=True)

    timezone = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.iso2_code} - {self.name}"
