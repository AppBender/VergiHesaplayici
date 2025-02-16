from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


@dataclass
class BaseModel:
    symbol: str
    date: datetime
    amount_usd: Decimal
    amount_tl: Decimal
    exchange_rate: Decimal
    description: str

    def to_csv_row(self) -> List[str]:
        """Convert the model to a CSV row"""
        raise NotImplementedError
