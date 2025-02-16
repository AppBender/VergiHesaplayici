from utils.utils import parse_numeric
from dataclasses import dataclass
from decimal import Decimal
from .base_model import BaseModel
from datetime import datetime
from typing import List


@dataclass
class Trade(BaseModel):
    quantity: Decimal
    buy_date: datetime
    sell_date: datetime
    is_option: bool

    def to_csv_row(self) -> List[str]:
        return [
            'Opsiyon' if self.is_option else 'Hisse Senedi',
            self.symbol,
            self.buy_date.strftime('%Y-%m-%d'),
            self.sell_date.strftime('%Y-%m-%d'),
            self.description,
            f"{self.quantity:.2f}",
            f"{self.amount_usd:.2f}",
            f"{self.exchange_rate:.4f}",
            f"{self.amount_tl:.2f}",
            'Alım-Satım'
        ]
