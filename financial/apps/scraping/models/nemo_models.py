from django.db import models


class NemotechModel(models.Model):
    nemo = models.CharField(max_length=255)
    green_bonus = models.FloatField(null=True)
    djsi = models.FloatField(null=True)
    etfs_foreign = models.CharField(max_length=1)
    isin = models.CharField(max_length=255)
    coin = models.CharField(max_length=10)
    amount = models.FloatField(null=True)
    weight = models.FloatField(null=True)
    close_price = models.FloatField(null=True)
    buy_price = models.FloatField(null=True)
    sell_price = models.FloatField(null=True)
    traded_units = models.FloatField(null=True)
    variant = models.FloatField(null=True)
