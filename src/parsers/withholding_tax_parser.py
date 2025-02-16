from datetime import datetime
from decimal import Decimal
from typing import List
import pandas as pd
from protocols.parser_protocol import ParserProtocol
from models.domains.withholding_tax import WithholdingTax
from utils.exchange_rate import get_exchange_rate
from services.logger_service import LoggerService


class WithholdingTaxParser(ParserProtocol[WithholdingTax]):
    def __init__(self):
        self.logger = LoggerService.get_instance()

    def can_parse(self, section_name: str) -> bool:
        return section_name in ["Withholding Tax", "Fees"]

    def parse(self, df: pd.DataFrame) -> List[WithholdingTax]:
        taxes = []
        for _, row in df.iterrows():
            try:
                if row.iloc[1] == "Data":
                    # Total satırını atla
                    if row.iloc[2] == "Total":
                        continue

                    date = datetime.strptime(str(row.iloc[3]), '%Y-%m-%d')
                    exchange_rate = get_exchange_rate(date)
                    amount = Decimal(str(row.iloc[5]))

                    tax = WithholdingTax(
                        symbol=row.iloc[4].split('(')[0].strip(),
                        date=date,
                        amount_usd=amount,
                        amount_tl=amount * Decimal(str(exchange_rate)),
                        exchange_rate=Decimal(str(exchange_rate)),
                        description='Temettü Stopajı'
                    )
                    taxes.append(tax)
            except Exception as e:
                error_msg = f"Stopaj satırı işlenirken hata: {str(e)}\nSatır verisi: {row.tolist()}"
                self.logger.log_error(error_msg)
                continue

        return taxes
