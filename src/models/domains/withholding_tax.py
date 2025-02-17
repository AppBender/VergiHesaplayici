from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from .base_model import BaseModel


@dataclass
class WithholdingTax(BaseModel):
    symbol: str    # Description'dan parse ediliyor

    def to_csv_row(self) -> List[str]:
        return [
            'Stopaj',
            self.symbol,
            self.date.strftime('%Y-%m-%d'),
            '',  # Satış tarihi yok
            'Temettü Stopajı',
            '',  # Miktar yok
            self.format_amount(self.amount_usd),
            f"{self.exchange_rate:.4f}",
            self.format_amount(self.amount_tl),
            'Stopaj'
        ]
