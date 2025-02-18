from .base_model import BaseModel
from dataclasses import dataclass
from typing import List


@dataclass
class WithholdingTax(BaseModel):
    symbol: str    # Description'dan parse ediliyor

    def to_csv_row(self) -> List[str]:
        return [
            'Stopaj',
            self.symbol,
            self.date.strftime('%Y-%m-%d'),
            'Temettü Stopajı',
            '',  # No sale date
            '',  # No quantity
            self.format_amount(self.amount_usd),
            f"{self.exchange_rate:.4f}",
            self.format_amount(self.amount_tl),
            'Stopaj'
        ]
