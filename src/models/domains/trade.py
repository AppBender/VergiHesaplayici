from .base_model import BaseModel
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List


@dataclass
class Trade(BaseModel):
    symbol: str           # Symbol
    quantity: Decimal     # Quantity
    buy_date: datetime    # Purchase date
    sell_date: datetime   # Date/Time (sale date)
    is_option: bool       # Determined from Asset Category
    commission: Decimal   # Comm/Fee

    def to_csv_row(self) -> List[str]:
        return [
            "Hisse Senedi" if not self.is_option else "Opsiyon",
            self.symbol,
            self.buy_date.strftime('%Y-%m-%d'),
            self.sell_date.strftime('%Y-%m-%d'),
            self.description,
            str(self.quantity),           # Remove :.2f formatting
            str(self.amount_usd),         # Remove :.2f formatting
            str(self.exchange_rate),      # Remove :.2f formatting
            str(self.amount_tl),          # Remove :.2f formatting
            "Alım-Satım"
        ]
