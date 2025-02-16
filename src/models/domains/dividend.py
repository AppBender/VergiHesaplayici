from utils.utils import parse_numeric
from dataclasses import dataclass
from decimal import Decimal
from .base_model import BaseModel


@dataclass
class Dividend(BaseModel):
    def __init__(self, row):
        self.currency = row.iloc[2]
        self.date_time = str(row.iloc[3])  # Ensure date_time is a string
        self.symbol = row.iloc[4]
        self.amount = float(row.iloc[5])

    def to_csv_row(self) -> list[str]:
        return [
            'Temettü',
            self.symbol,
            self.date.strftime('%Y-%m-%d'),
            '',  # No sell date for dividends
            'Brüt Temettü',
            f"{self.amount_usd:.2f}",
            f"{self.exchange_rate:.4f}",
            f"{self.amount_tl:.2f}",
            'Temettü'
        ]

# Dividends,Header,Currency,Date,Description,Amount,,,,,,,,,,,
# Dividends,Data,USD,2024-12-03,TBIL(US74933W4520) Cash Dividend USD 0.184283 per Share (Ordinary Dividend),19.03,,,,,,,,,,,
