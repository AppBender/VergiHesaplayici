import pandas as pd

from datetime import datetime
from decimal import Decimal
from typing import List, Dict
from models.domains.trade import Trade
from protocols.parser_protocol import ParserProtocol
from services.logger_service import LoggerService
from utils.exchange_rate import get_exchange_rate


class TradeParser(ParserProtocol[Trade]):
    def __init__(self):
        self.logger = LoggerService()
        self.current_order_is_sell = False  # Track if current Order is a sell

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Trades"

    def parse(self, df: pd.DataFrame) -> List[Trade]:
        trades: List[Trade] = []
        current_trade = None
        closed_lots: List[Dict] = []

        for _, row in df.iterrows():
            try:
                if row.iloc[1] != "Data":
                    continue

                discriminator = row.iloc[2]

                if discriminator == "Order":
                    # Check if this is a sell order (negative quantity)
                    quantity = Decimal(str(row.iloc[8]))
                    self.current_order_is_sell = quantity < 0

                elif discriminator == "Trade" and self.current_order_is_sell:
                    # Process trades only for sell orders
                    if current_trade and closed_lots:
                        trades.extend(self._create_trades_from_lots(current_trade, closed_lots))
                        closed_lots = []
                    elif current_trade:
                        trades.append(self._create_single_trade(current_trade))

                    current_trade = self._parse_trade_row(row)

                elif discriminator == "ClosedLot" and self.current_order_is_sell:
                    closed_lots.append({
                        'quantity': Decimal(str(row.iloc[8])),
                        'buy_date': datetime.strptime(str(row.iloc[6]), '%Y-%m-%d'),
                        'basis': Decimal(str(row.iloc[12])),
                        'realized_pl': Decimal(str(row.iloc[13]))  # Add realized P/L
                    })

            except Exception as e:
                self.logger.log_error(f"Trade parsing error: {str(e)}\nRow data: {row.tolist()}")
                continue

        # Process last trade if exists and it's a sell
        if self.current_order_is_sell:
            if current_trade and closed_lots:
                trades.extend(self._create_trades_from_lots(current_trade, closed_lots))
            elif current_trade:
                trades.append(self._create_single_trade(current_trade))

        return trades

    def _create_trades_from_lots(self, trade_data: Dict, closed_lots: List[Dict]) -> List[Trade]:
        result = []
        exchange_rate = get_exchange_rate(trade_data['sell_date'])

        for lot in closed_lots:
            realized_pl = lot['realized_pl']

            trade = Trade(
                symbol=trade_data['symbol'],
                date=lot['buy_date'],
                amount_usd=realized_pl,  # Using realized_pl consistently
                amount_tl=realized_pl * Decimal(str(exchange_rate)),
                exchange_rate=Decimal(str(exchange_rate)),
                description='Satış Karı' if realized_pl > 0 else 'Satış Zararı',
                quantity=-lot['quantity'],
                buy_date=lot['buy_date'],
                sell_date=trade_data['sell_date'],
                is_option=trade_data['is_option'],
                commission=trade_data['commission'] * abs(lot['quantity'] / trade_data['quantity'])
            )
            result.append(trade)

        return result

    def _parse_trade_row(self, row) -> Dict:
        return {
            'symbol': str(row.iloc[5]),
            'sell_date': datetime.strptime(str(row.iloc[6]).split(',')[0], '%Y-%m-%d'),
            'quantity': Decimal(str(row.iloc[8])),
            'realized_pl': Decimal(str(row.iloc[13])),  # Using consistent key name
            'commission': Decimal(str(row.iloc[11])),
            'is_option': 'Option' in str(row.iloc[3])
        }

    def _create_single_trade(self, trade_data: Dict) -> Trade:
        exchange_rate = get_exchange_rate(trade_data['sell_date'])

        return Trade(
            symbol=trade_data['symbol'],
            date=trade_data['sell_date'],
            amount_usd=trade_data['realized_pl'],  # Using realized_pl instead of amount
            amount_tl=trade_data['realized_pl'] * Decimal(str(exchange_rate)),
            exchange_rate=Decimal(str(exchange_rate)),
            description='Satış Karı' if trade_data['realized_pl'] > 0 else 'Satış Zararı',
            quantity=trade_data['quantity'],
            buy_date=trade_data['sell_date'],
            sell_date=trade_data['sell_date'],
            is_option=trade_data['is_option'],
            commission=trade_data['commission']
        )
