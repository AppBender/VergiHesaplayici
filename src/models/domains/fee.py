from .base_model import BaseModel
from dataclasses import dataclass
from typing import List


@dataclass
class Fee(BaseModel):
    symbol: str = ""    # Description'dan parse ediliyor

    def to_csv_row(self) -> List[str]:
        return [
            'Ücret',
            self.symbol,  # Artık symbol bilgisini gösteriyoruz
            self.date.strftime('%Y-%m-%d'),
            '',  # Satış tarihi yok
            self.description,
            '',  # Miktar yok
            self.format_amount(self.amount_usd),
            f"{self.exchange_rate:.4f}",
            self.format_amount(self.amount_tl),
            'Ücret'
        ]

# Fees,Header,Subtitle,Currency,Date,Description,Amount,,,,,,,,,,
# Fees,Data,Other Fees,USD,2024-12-03,E*******R3:CBOE ONE ADD-ON FOR NOV 2024,1,,,,,,,,,,
