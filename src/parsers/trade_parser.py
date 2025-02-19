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
        self.current_order_is_sell = False
        self.current_order_amount = Decimal('0')  # Track order total
        self.is_short_sale = False  # Track if this is a short sale

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Trades"

    def parse(self, df: pd.DataFrame) -> List[Trade]:
        trades: List[Trade] = []
        current_trade = None
        closed_lots: List[Dict] = []

        for _, row in df.iterrows():
            try:
                if row.iloc[1] != "Data":
                    if row.iloc[0] == "SubTotal":
                        # Verify against subtotal
                        reported_total = Decimal(str(row.iloc[13]))  # Realized P/L column
                        if current_trade and abs(self.current_order_amount - reported_total) > Decimal('0.01'):
                            self.logger.log_error(f"Amount mismatch: calculated {self.current_order_amount}, reported {reported_total}")
                        self.current_order_amount = Decimal('0')  # Reset for next order
                    continue

                discriminator = row.iloc[2]

                if discriminator == "Order":
                    quantity = Decimal(str(row.iloc[8]))
                    self.current_order_is_sell = quantity < 0
                    self.is_short_sale = 'Option' in str(row.iloc[3]) and quantity > 0  # Positive quantity for options might indicate short sale

                elif discriminator == "Trade":
                    # Process previous trade if exists
                    if current_trade and closed_lots:
                        new_trades = self._create_trades_from_lots(current_trade, closed_lots, self.is_short_sale)
                        trades.extend(new_trades)
                        self.current_order_amount += sum(t.amount_usd for t in new_trades)
                        closed_lots = []
                    elif current_trade:
                        trade = self._create_single_trade(current_trade)
                        trades.append(trade)
                        self.current_order_amount += trade.amount_usd

                    current_trade = self._parse_trade_row(row)

                elif discriminator == "ClosedLot":
                    if (self.current_order_is_sell and not self.is_short_sale) or \
                       (not self.current_order_is_sell and self.is_short_sale):
                        closed_lots.append({
                            'quantity': Decimal(str(row.iloc[8])),
                            'buy_date': datetime.strptime(str(row.iloc[6]), '%Y-%m-%d'),
                            'basis': Decimal(str(row.iloc[12])),
                            'realized_pl': Decimal(str(row.iloc[13]))
                        })

            except Exception as e:
                self.logger.log_error(f"Trade parsing error: {str(e)}\nRow data: {row.tolist()}")
                continue

        # Process last trade
        if current_trade and closed_lots:
            trades.extend(self._create_trades_from_lots(current_trade, closed_lots, self.is_short_sale))
        elif current_trade:
            trades.append(self._create_single_trade(current_trade))

        return trades

    def _create_trades_from_lots(self, trade_data: Dict, closed_lots: List[Dict], is_short: bool) -> List[Trade]:
        result = []

        for lot in closed_lots:
            realized_pl = lot['realized_pl']
            if is_short:
                buy_date = trade_data['sell_date']
                sell_date = lot['buy_date']
                buy_rate = get_exchange_rate(buy_date)
                sell_rate = get_exchange_rate(sell_date)
            else:
                buy_date = lot['buy_date']
                sell_date = trade_data['sell_date']
                buy_rate = get_exchange_rate(buy_date)
                sell_rate = get_exchange_rate(sell_date)

            trade = Trade(
                symbol=trade_data['symbol'],
                date=buy_date,
                amount_usd=realized_pl,
                amount_tl=realized_pl * Decimal(str(sell_rate)),
                exchange_rate=Decimal(str(sell_rate)),
                buy_exchange_rate=Decimal(str(buy_rate)),
                description='Satış Karı' if realized_pl > 0 else 'Satış Zararı',
                quantity=-lot['quantity'] if not is_short else lot['quantity'],
                buy_date=buy_date,
                sell_date=sell_date,
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
        sell_date = trade_data['sell_date']
        sell_rate = get_exchange_rate(sell_date)
        buy_rate = sell_rate  # For single trades, buy_date = sell_date so rates are same

        return Trade(
            symbol=trade_data['symbol'],
            date=sell_date,
            amount_usd=trade_data['realized_pl'],
            amount_tl=trade_data['realized_pl'] * Decimal(str(sell_rate)),
            exchange_rate=Decimal(str(sell_rate)),
            buy_exchange_rate=Decimal(str(buy_rate)),
            description='Satış Karı' if trade_data['realized_pl'] > 0 else 'Satış Zararı',
            quantity=trade_data['quantity'],
            buy_date=sell_date,
            sell_date=sell_date,
            is_option=trade_data['is_option'],
            commission=trade_data['commission']
        )
