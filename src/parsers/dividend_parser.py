import pandas as pd

from datetime import datetime
from decimal import Decimal
from models.domains.dividend import Dividend
from protocols.parser_protocol import ParserProtocol
from services.logger_service import LoggerService
from services.evds_service import EvdsService
from typing import List


class DividendParser(ParserProtocol[Dividend]):
    def __init__(self):
        self.logger = LoggerService.get_instance()
        self.evds_service = EvdsService()

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Dividends"

    def parse(self, df: pd.DataFrame) -> List[Dividend]:
        dividends = []
        for _, row in df.iterrows():
            try:
                if row.iloc[1] == "Data" and row.iloc[2] == "USD":
                    # Skip Total row
                    if "Total" in str(row.iloc[2]):
                        continue

                    date = datetime.strptime(str(row.iloc[3]), '%Y-%m-%d')
                    symbol = str(row.iloc[4]).split('(')[0].strip()
                    amount = Decimal(str(row.iloc[5]))
                    exchange_rate = self.evds_service.get_exchange_rate(date)

                    dividend = Dividend(
                        symbol=symbol,
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        taxable_amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description='Brüt Temettü'
                    )
                    dividends.append(dividend)
            except Exception as e:
                self.logger.log_error(f"Dividend parser error: {str(e)}\nRow data: {row.tolist()}")
                continue

        return dividends
