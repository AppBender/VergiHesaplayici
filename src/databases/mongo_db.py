import datetime
import os

from databases.database import Database
from pymongo import MongoClient


class MongoDB(Database):
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGODB_URI'))
        self.db = self.client.db
        self.logs = self.db.logs
        self.errors = self.db.errors

    def log_request(self, info: dict):
        info_copy = info.copy()
        info_copy["type"] = "request"
        info_copy["timestamp"] = datetime.datetime.now()
        self.logs.insert_one(info_copy)

    def log_response(self, info: dict):
        info_copy = info.copy()
        info_copy["type"] = "response"
        info_copy["timestamp"] = datetime.datetime.now()
        self.logs.insert_one(info_copy)

    def log_error(self, info: dict):
        info_copy = info.copy()
        info_copy["type"] = "error"
        info_copy["timestamp"] = datetime.datetime.now()
        self.errors.insert_one(info_copy)
