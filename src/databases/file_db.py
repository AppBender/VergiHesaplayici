import os
from datetime import datetime
from databases.database import Database


class FileDB(Database):
    def __init__(self, log_file='output/logs.txt'):
        self.log_file = log_file

    def clear_logs(self) -> bool:
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                return True
            return False
        except Exception as e:
            self.log_error(f"Failed to clear logs: {str(e)}")
            return False

    def _write_log(self, message: str, log_type: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'[{timestamp}] {log_type}: {message}\n')

    def log_info(self, info_message: str):
        self._write_log(f"{info_message}", "INFO")

    def log_error(self, error_message: str):
        self._write_log(f"Error: {error_message}", "ERROR")
