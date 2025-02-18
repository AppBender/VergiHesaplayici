from typing import Protocol


# Define the Database Protocol
class Database(Protocol):
    def log_info(self, info: dict):
        pass

    def log_error(self, info: dict):
        pass

    def save_exchange_rate(self, date: str, rate: float):
        pass

    def get_exchange_rate(self, date: str) -> float:
        pass
