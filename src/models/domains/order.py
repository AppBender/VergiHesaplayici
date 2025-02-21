from decimal import Decimal
from typing import List
from .trade import Trade


class Order:
    def __init__(self, symbol: str, quantity: Decimal, is_option: bool):
        self.symbol = symbol
        self.quantity = quantity
        self.is_sell = quantity < 0
        self.is_option = is_option
        self.trades: List[Trade] = []

    def add_trade(self, trade: Trade):
        self.trades.append(trade)