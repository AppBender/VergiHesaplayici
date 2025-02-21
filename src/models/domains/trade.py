from .base_model import BaseModel
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Dict


class Trade:
    def __init__(self,
                 symbol: str,
                 date: datetime,
                 amount_usd: Decimal,
                 quantity: Decimal,
                 commission: Decimal,
                 is_option: bool,
                 buy_date: datetime = None,
                 sell_date: datetime = None,
                 buy_exchange_rate: Decimal = None,
                 exchange_rate: Decimal = None,
                 buy_amount_tl: Decimal = None,
                 sell_amount_tl: Decimal = None,
                 buy_price: Decimal = None,    # Add buy price
                 sell_price: Decimal = None):  # Add sell price

        self.symbol = symbol
        self.date = date
        self.amount_usd = amount_usd
        self.quantity = quantity
        self.commission = commission
        self.is_option = is_option
        self.closed_lots: List[Dict] = []

        # Position dates
        self.buy_date = buy_date or date
        self.sell_date = sell_date or date

        # Exchange rates and TL amounts
        self.buy_exchange_rate = buy_exchange_rate
        self.exchange_rate = exchange_rate
        self.buy_amount_tl = buy_amount_tl
        self.sell_amount_tl = sell_amount_tl
        self.amount_tl = self.sell_amount_tl - self.buy_amount_tl if (self.sell_amount_tl and self.buy_amount_tl) else None

        # Description
        self.description = 'Satış Karı' if amount_usd > 0 else 'Satış Zararı'

        self.buy_price = buy_price
        self.sell_price = sell_price

    def add_closed_lot(self, lot: Dict):
        self.closed_lots.append(lot)

    @property
    def realized_pl(self) -> Decimal:
        return self.amount_usd

    def to_csv_row(self) -> List[str]:
        return [
            "Hisse Senedi" if not self.is_option else "Opsiyon",
            self.symbol,
            self.buy_date.strftime('%Y-%m-%d'),
            self.sell_date.strftime('%Y-%m-%d'),
            self.description,
            f"{self.quantity:.4f}",                # 4 decimals for quantity
            f"{self.amount_usd:.2f}",             # 2 decimals for USD
            f"{self.buy_price:.2f}",              # 2 decimals for prices
            f"{self.sell_price:.2f}",
            f"{self.buy_exchange_rate:.4f}",      # 4 decimals for exchange rates
            f"{self.exchange_rate:.4f}",
            f"{self.buy_amount_tl:.2f}",          # 2 decimals for TL amounts
            f"{self.sell_amount_tl:.2f}",
            f"{self.amount_tl:.2f}",
            "Alım-Satım"
        ]
