from .base_model import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List, Dict


class Trade(BaseModel):
    def __init__(
        self,
        symbol: str,
        date: datetime,
        amount_usd: Decimal,
        quantity: Decimal,
        commission: Decimal,
        is_option: bool,
        price: Decimal,
        buy_date: datetime = None,
        sell_date: datetime = None,
        buy_exchange_rate: Decimal = None,
        exchange_rate: Decimal = None,
        buy_amount_tl: Decimal = None,
        sell_amount_tl: Decimal = None,
        buy_price: Decimal = None,
        sell_price: Decimal = None,
        is_short: bool = False,
        yiufe_rate: Decimal = None
    ):
        self.symbol = symbol
        self.date = date
        self.amount_usd = amount_usd
        self.quantity = quantity
        self.commission = abs(commission)
        self.commission_tl = abs(commission * exchange_rate) if (commission and exchange_rate) else None
        self.is_option = is_option
        self.price = price
        self.buy_date = buy_date or date
        self.sell_date = sell_date or date
        self.closed_lots: List[Dict] = []
        self.buy_exchange_rate = buy_exchange_rate
        self.exchange_rate = exchange_rate
        self.buy_amount_tl = buy_amount_tl
        self.sell_amount_tl = sell_amount_tl
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.yiufe_rate = yiufe_rate

        is_profit = amount_usd > 0

        if is_short:
            self.description = '(Açığa) Satış Karı' if is_profit else '(Açığa) Satış Zararı'
        else:
            self.description = 'Satış Karı' if is_profit else 'Satış Zararı'

        # Calculate TL profit/loss including commission
        self.amount_tl = (self.sell_amount_tl - self.buy_amount_tl - self.commission_tl) if (
            self.sell_amount_tl and
            self.buy_amount_tl and
            self.commission_tl
        ) else None

        # Apply YI-ÜFE indexing to buy amount if applicable
        self.indexed_buy_amount_tl = self._calculate_indexed_buy_amount()

        # Calculate final taxable amount
        self.taxable_amount_tl = self._calculate_taxable_amount()

    def _calculate_indexed_buy_amount(self) -> Decimal:
        """Calculate indexed buy amount based on YI-ÜFE rate if applicable"""
        should_apply_indexing = (
            self.yiufe_rate is not None and
            self.yiufe_rate > 10 and
            self.buy_amount_tl is not None
        )

        if should_apply_indexing:
            indexing_multiplier = 1 + (self.yiufe_rate / 100)
            return self.buy_amount_tl * indexing_multiplier

        return self.buy_amount_tl

    def _calculate_taxable_amount(self) -> Decimal:
        """Calculate taxable amount considering indexed buy amount and commission"""
        required_values = [
            self.sell_amount_tl,
            self.indexed_buy_amount_tl,
            self.commission_tl
        ]

        if all(required_values):
            return (
                self.sell_amount_tl -
                self.indexed_buy_amount_tl -
                self.commission_tl
            )

        return None

    def add_closed_lot(self, lot: Dict):
        self.closed_lots.append(lot)

    @property
    def realized_pl(self) -> Decimal:
        return self.amount_usd

    def to_csv_row(self) -> List[str]:
        return [
            "Hisse Senedi" if not self.is_option else "Opsiyon",
            self.symbol,
            self.description,
            f"{self.quantity:.4f}",
            self.buy_date.strftime('%Y-%m-%d'),
            f"{self.buy_price:.2f}",
            f"{self.buy_exchange_rate:.4f}",
            self.sell_date.strftime('%Y-%m-%d'),
            f"{self.sell_price:.2f}",
            f"{self.exchange_rate:.4f}",
            f"{self.commission_tl:.2f}",
            f"{self.buy_amount_tl:.2f}",
            f"{self.sell_amount_tl:.2f}",
            f"{self.yiufe_rate:.2f}" if self.yiufe_rate > 10 else "-",
            f"{self.indexed_buy_amount_tl:.2f}",
            f"{self.taxable_amount_tl:.2f}",
            f"{self.amount_tl:.2f}",
            f"{self.amount_usd:.2f}",
            "Alım-Satım"
        ]
