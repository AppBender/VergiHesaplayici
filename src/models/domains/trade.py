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
            'Opsiyon' if self.is_option else 'Hisse Senedi',
            self.symbol,
            self.buy_date.strftime('%Y-%m-%d'),
            self.sell_date.strftime('%Y-%m-%d'),
            'Satış Karı' if self.amount_usd > 0 else 'Satış Zararı',
            self.format_amount(self.quantity),
            self.format_amount(self.amount_usd),
            f"{self.exchange_rate:.4f}",
            self.format_amount(self.amount_tl),
            'Alım-Satım'
        ]
