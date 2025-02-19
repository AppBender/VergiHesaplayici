from .base_model import BaseModel
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List


class Trade:
    def __init__(self,
                 symbol: str,
                 date: datetime,
                 amount_usd: Decimal,
                 amount_tl: Decimal,
                 exchange_rate: Decimal,
                 buy_exchange_rate: Decimal,  # Moved up and made required
                 description: str,
                 quantity: Decimal,
                 buy_date: datetime,
                 sell_date: datetime,
                 is_option: bool,
                 commission: Decimal):

        self.symbol = symbol
        self.date = date
        self.amount_usd = amount_usd
        self.exchange_rate = exchange_rate
        self.buy_exchange_rate = buy_exchange_rate
        self.description = description
        self.quantity = quantity
        self.buy_date = buy_date
        self.sell_date = sell_date
        self.is_option = is_option
        self.commission = commission

        # Avoid division by zero and handle None values
        try:
            price_per_unit = abs(amount_usd / quantity) if quantity != 0 else Decimal('0')
            self.buy_amount_tl = abs(self.quantity) * price_per_unit * buy_exchange_rate
            self.sell_amount_tl = abs(self.quantity) * price_per_unit * exchange_rate
            self.amount_tl = self.sell_amount_tl - self.buy_amount_tl
        except (TypeError, ZeroDivisionError) as e:
            raise ValueError(f"Error calculating TL amounts for {symbol}: {str(e)}")

    def to_csv_row(self) -> List[str]:
        return [
            "Hisse Senedi" if not self.is_option else "Opsiyon",
            self.symbol,
            self.buy_date.strftime('%Y-%m-%d'),
            self.sell_date.strftime('%Y-%m-%d'),
            self.description,
            f"{self.quantity:.4f}",                    # 4 decimal
            f"{self.amount_usd:.6f}",                  # 6 decimal
            f"{self.buy_exchange_rate:.4f}",           # 4 decimal
            f"{self.exchange_rate:.4f}",               # 4 decimal
            f"{self.buy_amount_tl:.2f}",              # 2 decimal
            f"{self.sell_amount_tl:.2f}",             # 2 decimal
            f"{self.amount_tl:.2f}",                  # 2 decimal
            "Alım-Satım"
        ]
