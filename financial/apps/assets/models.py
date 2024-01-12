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
    close = models.FloatField(null=True)
    adj_close = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    open = models.FloatField(null=True)
    volume = models.IntegerField(null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
