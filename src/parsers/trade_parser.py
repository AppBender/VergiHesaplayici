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
                    # DataFrame'den değerleri indeks ile alalım
                    date = datetime.strptime(str(row.iloc[6]).split(',')[0], '%Y-%m-%d')
                    symbol = row.iloc[5]
                    amount = Decimal(str(row.iloc[13]))  # realized_pl
                    exchange_rate = get_exchange_rate(date)

                    trade = Trade(
                        symbol=symbol,
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description='Satış Karı' if amount > 0 else 'Satış Zararı',
                        quantity=Decimal(str(row.iloc[8])),
                        buy_date=date,  # Şimdilik satış tarihi ile aynı
                        sell_date=date,
                        is_option='Option' in str(row.iloc[3])  # Asset Category'de 'Option' kelimesi varsa
                    )
                    trades.append(trade)
            except Exception as e:
                error_msg = f"Trade satırı işlenirken hata: {str(e)}\nSatır verisi: {row.tolist()}"
                self.logger.log_error(error_msg)
                continue

        return trades
