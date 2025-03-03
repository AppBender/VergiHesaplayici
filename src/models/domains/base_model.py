from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class BaseModel:
    date: datetime                  # Date information for all transactions
    description: str                # Description information for all transactions
    amount_usd: Decimal             # amount/proceeds value
    amount_tl: Decimal              # TRY equivalent (calculated)
    taxable_amount_tl: Decimal      # Taxale TRY equivalent (calculated)
    exchange_rate: Decimal          # Exchange rate (from TCMB)

    def format_amount(self, value: Decimal) -> str:
        return f"{value:.2f}" if value else "0.00"
