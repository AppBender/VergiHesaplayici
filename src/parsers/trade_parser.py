from datetime import datetime
from decimal import Decimal
from typing import List
import pandas as pd
from protocols.parser_protocol import ParserProtocol
from models.domains.trade import Trade
from utils.exchange_rate import get_exchange_rate
from services.logger_service import LoggerService


class TradeParser(ParserProtocol[Trade]):
    def __init__(self):
        self.logger = LoggerService.get_instance()

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Trades"

    def parse(self, df: pd.DataFrame) -> List[Trade]:
        trades = []
        for _, row in df.iterrows():
            try:
                if row.iloc[1] == "Data" and row.iloc[2] == "Trade":
                    if "Total" in str(row.iloc[2]):
                        continue

                    # Parse date and time
                    date_str = str(row.iloc[6]).split(',')[0]
                    date = datetime.strptime(date_str, '%Y-%m-%d')

                    # Get exchange rate
                    exchange_rate = get_exchange_rate(date)

                    # Parse amounts
                    amount = Decimal(str(row.iloc[13]))  # realized_pl
                    quantity = Decimal(str(row.iloc[8]))
                    commission = Decimal(str(row.iloc[11]))  # Comm/Fee

                    # Check if it's an option
                    is_option = 'Option' in str(row.iloc[3])

                    trade = Trade(
                        symbol=str(row.iloc[5]),
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description='Satış Karı' if amount > 0 else 'Satış Zararı',
                        quantity=quantity,
                        buy_date=date,
                        sell_date=date,
                        is_option=is_option,
                        commission=commission  # Add commission
                    )
                    trades.append(trade)

            except Exception as e:
                self.logger.log_error(f"Trade satırı işlenirken hata: {str(e)}\nSatır verisi: {row.tolist()}")
                continue

        return trades
