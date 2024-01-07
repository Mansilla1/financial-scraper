from dataclasses import dataclass


@dataclass
class GetNemoPriceResponseData:
    green_bonus: str
    djsi: str
    etfs_foreign: str
    isin: str
    coin: str
    amount: str
    nemo: str
    weight: str
    close_price: str
    buy_price: str
    sell_price: str
    traded_units: str
    variant: str

    def raw_serialize(self):
        return {
            'BONO_VERDE': self.green_bonus,
            'DJSI': self.djsi,
            'ETFs_EXTRANJERO': self.etfs_foreign,
            'ISIN': self.isin,
            'MONEDA': self.coin,
            'MONTO': self.amount,
            'NEMO': self.nemo,
            'PESO': self.weight,
            'PRECIO_CIERRE': self.close_price,
            'PRECIO_COMPRA': self.buy_price,
            'PRECIO_VENTA': self.sell_price,
            'UN_TRANSADAS': self.traded_units,
            'VARIACION': self.variant,
        }

    def serialize(self):
        return {
            'green_bonus': self.green_bonus,
            'djsi': self.djsi,
            'etfs_foreign': self.etfs_foreign,
            'isin': self.isin,
            'coin': self.coin,
            'amount': self.amount,
            'nemo': self.nemo,
            'weight': self.weight,
            'close_price': self.close_price,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'traded_units': self.traded_units,
            'variant': self.variant,
        }
