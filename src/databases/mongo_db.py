import datetime
import os

from databases.database import Database
from decimal import Decimal
from pymongo import MongoClient


class MongoDB(Database):
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGODB_URI'))
        self.db = self.client.vergi_hesaplayici_db
        self.info = self.db.info
        self.errors = self.db.errors
        self.exchange_rates = self.db.exchange_rates

    def log_info(self, info: dict):
        info_copy = info.copy()
        info_copy["type"] = "info"
        info_copy["timestamp"] = datetime.datetime.now()
        self.info.insert_one(info_copy)

    def log_error(self, info: dict):
        info_copy = info.copy()
        info_copy["type"] = "error"
        info_copy["timestamp"] = datetime.datetime.now()
        self.errors.insert_one(info_copy)

    def save_exchange_rate(self, date: str, rate: float):
        self.exchange_rates.insert_one({'date': date, 'rate': rate})

    def get_exchange_rate(self, date: str) -> float:
        rate = self.exchange_rates.find_one({'date': date})
        return rate['rate'] if rate else None

    def get_yiufe_index(self, date_str: str) -> Decimal:
        record = self.db['yiufe_indices'].find_one({'date': date_str})
        return Decimal(str(record['index'])) if record else None

    def save_yiufe_index(self, date_str: str, index: Decimal):
        self.db['yiufe_indices'].update_one(
            {'date': date_str},
            {
                '$set': {
                    'date': date_str,
                    'index': float(index),
                    'updated_at': datetime.datetime.now()
                }
            },
            upsert=True
        )
