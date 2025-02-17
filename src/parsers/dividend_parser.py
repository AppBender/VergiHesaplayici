import pandas as pd

from datetime import datetime
from decimal import Decimal
from models.domains.dividend import Dividend
from protocols.parser_protocol import ParserProtocol
from services.logger_service import LoggerService
from typing import List
from utils.exchange_rate import get_exchange_rate


class DividendParser(ParserProtocol[Dividend]):
    def __init__(self):
        self.logger = LoggerService.get_instance()

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Dividends"

    def parse(self, df: pd.DataFrame) -> List[Dividend]:
        dividends = []
        for _, row in df.iterrows():
            try:
                if row.iloc[1] == "Data" and row.iloc[2] == "USD":
                    # Total satırını atla
                    if "Total" in str(row.iloc[2]):
                        continue

                    date = datetime.strptime(str(row.iloc[3]), '%Y-%m-%d')
                    symbol = str(row.iloc[4]).split('(')[0].strip()
                    amount = Decimal(str(row.iloc[5]))
                    exchange_rate = get_exchange_rate(date)

                    dividend = Dividend(
                        symbol=symbol,
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description='Brüt Temettü'
                    )
                    dividends.append(dividend)
            except Exception as e:
                self.logger.log_error(f"Temettü satırı işlenirken hata: {str(e)}\nSatır verisi: {row.tolist()}")
                continue

        return dividends
