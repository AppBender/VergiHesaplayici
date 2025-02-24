from databases.file_db import FileDB
from typing import Optional
from datetime import datetime

LOG_PATH = 'logfile.log'

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

    def log_warning(self, message: str):
        """Log warning message"""
        self._log("WARNING", message)

    def _log(self, level: str, message: str):
        """Internal method to write log entry"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"

        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
