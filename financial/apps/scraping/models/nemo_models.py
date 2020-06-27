from django.db import models


class NemotechModel(models.Model):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DEAD = 'dead'

    STATUS_CHOICES = (
        (ACTIVE, 'Activo'),
        (INACTIVE, 'Inactivo'),
        (DEAD, 'Muerto'),
    )

    nemo = models.CharField(max_length=255)
    green_bonus = models.FloatField(null=True, help_text='BONO_VERDE')
    djsi = models.FloatField(null=True)
    etfs_foreign = models.CharField(max_length=1, help_text='ETFs_EXTRANJERO')
    isin = models.CharField(max_length=255)
    coin = models.CharField(max_length=10, help_text='MONEDA')
    amount = models.FloatField(null=True, help_text='MONTO')
    weight = models.FloatField(null=True, help_text='PESO')
    close_price = models.FloatField(null=True, help_text='PRECIO_CIERRE')
    buy_price = models.FloatField(null=True, help_text='PRECIO_COMRA')
    sell_price = models.FloatField(null=True, help_text='PRECIO_VENTA')
    traded_units = models.FloatField(null=True, help_text='UN_TRANSADAS')
    variant = models.FloatField(null=True, help_text='VARIACION')
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        null=False,
        help_text=(
            'It maintains the information in case of changes, '
            'the one that remains "active" will be the updated one.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nemo_tech'
