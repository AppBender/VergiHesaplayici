from .base_model import BaseModel
from dataclasses import dataclass
from typing import List


@dataclass
class Dividend(BaseModel):
    symbol: str

    def to_csv_row(self) -> List[str]:
        return [
            'Temettü',
            self.symbol,
            'Brüt Temettü',
            self.date.strftime('%Y-%m-%d'),
            self.format_amount(self.amount_usd),
            f"{self.exchange_rate:.4f}",
            self.format_amount(self.taxable_amount_tl),
            'Temettü'
        ]