from datetime import datetime
from decimal import Decimal
from typing import List
import pandas as pd
from protocols.parser_protocol import ParserProtocol
from models.domains.fee import Fee
from utils.exchange_rate import get_exchange_rate
from services.logger_service import LoggerService


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
                    # Total satırını atla
                    if row.iloc[2] == "Total":
                        continue

                    date = datetime.strptime(str(row.iloc[4]), '%Y-%m-%d')
                    exchange_rate = get_exchange_rate(date)
                    amount = Decimal(str(row.iloc[6]))

                    fee = Fee(
                        symbol="",  # Fee'lerde genelde symbol olmaz
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description=row.iloc[5]  # Fee açıklaması
                    )
                    fees.append(fee)
            except Exception as e:
                error_msg = f"Fee satırı işlenirken hata: {str(e)}\nSatır verisi: {row.tolist()}"
                self.logger.log_error(error_msg)
                continue

        return fees
