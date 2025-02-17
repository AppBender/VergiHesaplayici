from utils.utils import parse_numeric
from dataclasses import dataclass
from decimal import Decimal
from .base_model import BaseModel
from datetime import datetime
from typing import List


@dataclass
class Trade(BaseModel):
    symbol: str           # Symbol
    quantity: Decimal     # Quantity
    buy_date: datetime    # Alış tarihi
    sell_date: datetime   # Date/Time (satış tarihi)
    is_option: bool       # Asset Category'den belirleniyor
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
