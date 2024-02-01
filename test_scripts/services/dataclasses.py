import arrow

from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class SpotOperationDetail:
    currency: str
    proposedAmount: float
    proposedAmountUSD: float
    usdPrice: float
    rut: str
    operation: str
    transferPrice: str
    externalId: Optional[Union[str, int]] = None
    injected: Optional[bool] = False
    badResponse: Optional[str] = None

    @property
    def serialize(self):
        return {
            "currency": self.currency,
            "proposedAmount": self.proposedAmount,
            "proposedAmountUSD": self.proposedAmountUSD,
            "usdPrice": self.usdPrice,
            "rut": self.rut,
            "operation": self.operation,
            "transferPrice": self.transferPrice,
            "externalId": self.externalId,
            "injected": self.injected,
            "badResponse": self.badResponse,
        }


@dataclass
class SpotOperationData:
    injected: bool
    createdAt: Union[arrow.Arrow, datetime]
    sentToBuySellUSDDate: Union[arrow.Arrow, datetime]
    spotOperations: List[SpotOperationDetail]
    totalBuyDollars: float
    totalSellDollars: float

    @property
    def serialize(self):
        return {
            "injected": self.injected,
            "createdAt": self.createdAt,
            "sentToBuySellUSDDate": self.sentToBuySellUSDDate,
            "spotOperations": list(map(lambda x: x.serialize, self.spotOperations)),
            "totalBuyDollars": self.totalBuyDollars,
            "totalSellDollars": self.totalSellDollars,
        }


@dataclass
class DocumentInformationData:
    data: Dict
    sub_documents: List[str]


# voultech
@dataclass
class Movement:
    '''
    Example:
    {
        "id": 9265516,
        "codTipoMovimiento": "APO_PAT_RC",
        "numCuenta": "16838513/60",
        "tipoMovimiento": "A",
        "dscMovimiento": "APORTE PATRIMONIAL RC",
        "fechaMovimiento": "2023-12-19T00:00:00",
        "fechaLiquidacion": "2023-12-19T00:00:00",
        "monto": 9000.000000,
        "codMoneda": "USD",
        "dscCajaCuenta": "CAJA DOLAR",
        "dscEstadoMovimiento": "Liquidado"
    }
    '''
    id: int
    code_movement_type: str
    account_number: str
    movement_type: str
    description: str
    movement_date: Union[str, arrow.Arrow]
    settlement_date: Union[str, arrow.Arrow]
    amount: float
    currency_code: str
    account_description: str
    movement_status: str

    @property
    def serialize(self):
        return {
            "id": self.id,
            "codTipoMovimiento": self.code_movement_type,
            "numCuenta": self.account_number,
            "tipoMovimiento": self.movement_type,
            "dscMovimiento": self.description,
            "fechaMovimiento": self.movement_date.format("YYYY-MM-DDTHH:mm:ss") if isinstance(self.movement_date, arrow.Arrow) else self.movement_date,
            "fechaLiquidacion": self.settlement_date.format("YYYY-MM-DDTHH:mm:ss") if isinstance(self.settlement_date, arrow.Arrow) else self.settlement_date,
            "monto": self.amount,
            "codMoneda": self.currency_code,
            "dscCajaCuenta": self.account_description,
            "dscEstadoMovimiento": self.movement_status,
        }
