from utils.utils import parse_numeric
from dataclasses import dataclass
from decimal import Decimal
from .base_model import BaseModel


@dataclass
class Fee(BaseModel):
    def __init__(self, date, amount_usd, amount_tl, exchange_rate, description):
        super().__init__(
            symbol="",  # Fee'ler için symbol kullanmıyoruz
            date=date,
            amount_usd=amount_usd,
            amount_tl=amount_tl,
            exchange_rate=exchange_rate,
            description=description
        )

    def to_csv_row(self) -> list[str]:
        return [
            'Ücret',
            '',  # Symbol yok
            self.date.strftime('%Y-%m-%d'),
            '',  # Satış tarihi yok
            self.description,
            '',  # Miktar yok
            f"{self.amount_usd:.2f}",
            f"{self.exchange_rate:.4f}",
            f"{self.amount_tl:.2f}",
            'Ücret'
        ]

# Fees,Header,Subtitle,Currency,Date,Description,Amount,,,,,,,,,,
# Fees,Data,Other Fees,USD,2024-12-03,E*******R3:CBOE ONE ADD-ON FOR NOV 2024,1,,,,,,,,,,
