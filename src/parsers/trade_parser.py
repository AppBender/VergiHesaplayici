import pandas as pd

from datetime import datetime
from decimal import Decimal
from typing import List, Dict
from models.domains.trade import Trade
from models.domains.order import Order
from protocols.parser_protocol import ParserProtocol
from services.logger_service import LoggerService
from utils.exchange_rate import get_exchange_rate


class TradeParser(ParserProtocol[Trade]):
    def __init__(self):
        self.logger = LoggerService()

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Trades"

    def parse(self, df: pd.DataFrame) -> List[Trade]:
        trades: List[Trade] = []
        orders: List[Order] = []

        # First pass: Build the hierarchy
        current_order = None
        current_trade = None

        for _, row in df.iterrows():
            try:
                if row.iloc[1] != "Data":
                    continue

                discriminator = row.iloc[2]

                if discriminator == "Order":
                    current_order = Order(
                        symbol=str(row.iloc[5]),
                        quantity=Decimal(str(row.iloc[8])),
                        is_option='Option' in str(row.iloc[3])
                    )
                    orders.append(current_order)

                elif discriminator == "Trade":
                    current_trade = Trade(
                        symbol=str(row.iloc[5]),
                        date=datetime.strptime(str(row.iloc[6]).split(',')[0], '%Y-%m-%d'),
                        amount_usd=Decimal(str(row.iloc[13])),
                        quantity=Decimal(str(row.iloc[8])),
                        commission=Decimal(str(row.iloc[11])),
                        is_option='Option' in str(row.iloc[3]),
                        price=Decimal(str(row.iloc[9]))  # Add T.Price from column 9
                    )
                    if current_order:
                        current_order.add_trade(current_trade)

                elif discriminator == "ClosedLot":
                    if current_trade:
                        current_trade.add_closed_lot({
                            'quantity': Decimal(str(row.iloc[8])),
                            'buy_date': datetime.strptime(str(row.iloc[6]), '%Y-%m-%d'),
                            'basis': Decimal(str(row.iloc[12])),
                            'realized_pl': Decimal(str(row.iloc[13]))
                        })

            except Exception as e:
                self.logger.log_error(f"Trade parsing error: {str(e)}\nRow data: {row.tolist()}")
                continue

        # Second pass: Process only trades with ClosedLots
        for order in orders:
            for trade in order.trades:
                if trade.closed_lots:  # Only process if there are ClosedLots
                    new_trades = self._create_trades_from_lots(
                        trade_data={
                            'symbol': trade.symbol,
                            'sell_date': trade.sell_date,
                            'quantity': trade.quantity,
                            'realized_pl': trade.realized_pl,
                            'commission': trade.commission,
                            'is_option': trade.is_option,
                            'price': trade.price  # Add price from trade
                        },
                        closed_lots=trade.closed_lots,
                    )
                    trades.extend(new_trades)

        return trades

    def _create_trades_from_lots(self, trade_data: Dict, closed_lots: List[Dict]) -> List[Trade]:
        result = []

        for lot in closed_lots:
            quantity = abs(lot['quantity'])
            is_short = lot['quantity'] < 0

            # Calculate proportional commission for this lot
            lot_commission = trade_data['commission'] * abs(lot['quantity'] / trade_data['quantity'])

            if is_short:
                buy_date = trade_data['sell_date']
                sell_date = lot['buy_date']
                buy_price = trade_data['price']
                sell_price = Decimal(str(lot['basis'] / lot['quantity']))
            else:
                buy_date = lot['buy_date']
                sell_date = trade_data['sell_date']
                buy_price = Decimal(str(lot['basis'] / lot['quantity']))
                sell_price = trade_data['price']

            buy_rate = get_exchange_rate(buy_date)
            sell_rate = get_exchange_rate(sell_date)

            # Calculate amounts with commission
            buy_amount_tl = quantity * buy_price * Decimal(str(buy_rate))
            sell_amount_tl = quantity * sell_price * Decimal(str(sell_rate))

            trade = Trade(
                symbol=trade_data['symbol'],
                date=buy_date,
                amount_usd=lot['realized_pl'],
                quantity=-lot['quantity'] if not is_short else lot['quantity'],
                commission=lot_commission,     # Store proportional commission
                is_option=trade_data['is_option'],
                price=trade_data['price'],
                buy_date=buy_date,
                sell_date=sell_date,
                buy_exchange_rate=Decimal(str(buy_rate)),
                exchange_rate=Decimal(str(sell_rate)),  # Use sell_rate for commission
                buy_amount_tl=buy_amount_tl,
                sell_amount_tl=sell_amount_tl,
                buy_price=buy_price,
                sell_price=sell_price,
                is_short=is_short
            )
            result.append(trade)

        return result
