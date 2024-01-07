from django.db import models

from financial.apps.utils.models import UUIDBaseModel


class Currency(UUIDBaseModel):
    code = models.CharField(max_length=10, blank=False, null=False)
    name = models.CharField(max_length=70, blank=False, null=False)

    status = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class CurrencyPrice(UUIDBaseModel):
    currency = models.ForeignKey(
        "currency.Currency", on_delete=models.DO_NOTHING, null=False
    )
    price = models.FloatField(null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
