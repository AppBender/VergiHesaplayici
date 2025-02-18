import pandas as pd

from datetime import datetime
from decimal import Decimal
from models.domains.fee import Fee
from protocols.parser_protocol import ParserProtocol
from services.logger_service import LoggerService
from typing import List
from utils.exchange_rate import get_exchange_rate


class FeeParser(ParserProtocol[Fee]):
    def __init__(self):
        self.logger = LoggerService.get_instance()

    def can_parse(self, section_name: str) -> bool:
        return section_name == "Fees"

    def parse(self, df: pd.DataFrame) -> List[Fee]:
        fees = []
        for _, row in df.iterrows():
            try:
                if row.iloc[1] == "Data" and row.iloc[2] == "Other Fees":
                    # Skip Total row
                    if "Total" in str(row.iloc[2]):
                        continue

                    date = datetime.strptime(str(row.iloc[4]), '%Y-%m-%d')
                    description = str(row.iloc[5])
                    # Symbol'u description'dan çıkar (eğer varsa)
                    symbol = description.split(':')[0] if ':' in description else ""
                    amount = Decimal(str(row.iloc[6]))
                    exchange_rate = get_exchange_rate(date)

                    fee = Fee(
                        symbol=symbol,
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description=description
                    )
                    fees.append(fee)
            except Exception as e:
                self.logger.log_error(f"Fee satırı işlenirken hata: {str(e)}\nSatır verisi: {row.tolist()}")
                continue

        return fees
