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

    def save_exchange_rate(self, date: str, rate: Decimal):
        """Save exchange rate to MongoDB only if it doesn't exist"""
        try:
            # Check if rate already exists
            existing_rate = self.exchange_rates.find_one({'date': date})
            if existing_rate:
                return  # Skip if already exists

            # Insert new rate
            self.exchange_rates.insert_one({
                'date': date,
                'rate': float(rate),
                'created_at': datetime.datetime.now()
            })
        except Exception as e:
            self.log_error({
                "message": f"Error saving exchange rate: {str(e)}",
                "date": date,
                "rate": str(rate)
            })
            raise

    def get_exchange_rate(self, date: str) -> float:
        rate = self.exchange_rates.find_one({'date': date})
        return rate['rate'] if rate else None

    def get_yiufe_index(self, date_str: str) -> Decimal:
        record = self.db['yiufe_indices'].find_one({'date': date_str})
        return Decimal(str(record['index'])) if record else None

    def save_yiufe_index(self, date_str: str, index: Decimal):
        """Save YI-ÜFE index to MongoDB only if it doesn't exist"""
        try:
            # Check if index already exists
            existing_index = self.db['yiufe_indices'].find_one({'date': date_str})
            if existing_index:
                return  # Skip if already exists

            # Insert new index
            self.db['yiufe_indices'].insert_one({
                'date': date_str,
                'index': float(index),
                'created_at': datetime.datetime.now()
            })
        except Exception as e:
            self.log_error({
                "message": f"Error saving YI-ÜFE index: {str(e)}",
                "date": date_str,
                "index": str(index)
            })
            raise
