from dataclasses import dataclass
from decimal import Decimal
from .base_model import BaseModel


@dataclass
class WithholdingTax(BaseModel):
    def to_csv_row(self) -> list[str]:
        return [
            'Stopaj',
            self.symbol,
            self.date.strftime('%Y-%m-%d'),
            '',  # No sell date for withholding tax
            'Temettü Stopajı',
            f"{self.amount_usd:.2f}",
            f"{self.exchange_rate:.4f}",
            f"{self.amount_tl:.2f}",
            'Stopaj'
        ]