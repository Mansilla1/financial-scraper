from django.db import models

from financial.apps.utils.models import UUIDBaseModel


class Asset(UUIDBaseModel):
    name = models.CharField(max_length=255)
    ticker = models.CharField(max_length=255)
    description = models.TextField(null=True)
    currency = models.CharField(max_length=3)
    country = models.ForeignKey("geo.Country", on_delete=models.DO_NOTHING, null=True)
    active = models.BooleanField(default=True)


class AssetPrice(UUIDBaseModel):
    asset = models.ForeignKey("assets.Asset", on_delete=models.DO_NOTHING, null=False)
    price = models.FloatField(null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
