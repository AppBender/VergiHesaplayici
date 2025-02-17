from .base_model import BaseModel
from dataclasses import dataclass
from typing import List


@dataclass
class Dividend(BaseModel):
    symbol: str    # Description'dan parse ediliyor - TBIL(US74933W4520)

    def to_csv_row(self) -> List[str]:
        return [
            'Temettü',
            self.symbol,
            self.date.strftime('%Y-%m-%d'),
            '',  # Satış tarihi yok
            'Brüt Temettü',
            '',  # Miktar yok
            self.format_amount(self.amount_usd),
            f"{self.exchange_rate:.4f}",
            self.format_amount(self.amount_tl),
            'Temettü'
        ]

# Dividends,Header,Currency,Date,Description,Amount,,,,,,,,,,,
# Dividends,Data,USD,2024-12-03,TBIL(US74933W4520) Cash Dividend USD 0.184283 per Share (Ordinary Dividend),19.03,,,,,,,,,,,
