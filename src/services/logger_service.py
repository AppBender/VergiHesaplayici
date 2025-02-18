from databases.file_db import FileDB
from typing import Optional


class LoggerService:
    _instance: Optional['LoggerService'] = None

    def __init__(self):
        self.db = FileDB()

    @classmethod
    def get_instance(cls) -> 'LoggerService':
        if cls._instance is None:
            cls._instance = LoggerService()
        return cls._instance

    def log_error(self, message: str):
        self.db.log_error(message)

    def log_info(self, message: str):
        self.db.log_info(message)
