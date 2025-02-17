from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class BaseModel:
    date: datetime          # Tüm işlemlerin tarih bilgisi var
    description: str        # Tüm işlemlerin açıklama bilgisi var
    amount_usd: Decimal     # amount/proceeds değeri
    amount_tl: Decimal      # TL karşılığı (hesaplanıyor)
    exchange_rate: Decimal  # Kur bilgisi (TCMB'den alınıyor)

    def format_amount(self, value: Decimal) -> str:
        return f"{value:.2f}" if value else "0.00"
