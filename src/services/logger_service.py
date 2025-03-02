from typing import Optional
from datetime import datetime

ERROR_LOG_PATH = 'output/error.log'
INFO_LOG_PATH = 'output/info.log'
WARNING_LOG_PATH = 'output/warning.log'


class LoggerService:
    _instance: Optional['LoggerService'] = None

    @classmethod
    def get_instance(cls) -> 'LoggerService':
        if cls._instance is None:
            cls._instance = LoggerService()
        return cls._instance

    def log_error(self, message: str):
        self._log("ERROR", message, ERROR_LOG_PATH)

    def log_info(self, message: str):
        self._log("INFO", message, INFO_LOG_PATH)

    def log_warning(self, message: str):
        """Log warning message"""
        self._log("WARNING", message, WARNING_LOG_PATH)

    def _log(self, level: str, message: str, file_path: str):
        """Internal method to write log entry"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
