import os
from datetime import datetime
from databases.database import Database


class FileDB(Database):
    def __init__(self, log_file='logs.txt'):
        # Get project root directory (2 levels up from file_db.py)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.log_file = os.path.join(project_root, log_file)

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
            # log = f"[{timestamp}] {log_type}: {message}\n"
            log = f"{message}"
            f.write(f"{log}\n")
            print(log)

    def log_info(self, info_message: str):
        self._write_log(f"{info_message}", "INFO")

    def log_error(self, error_message: str):
        self._write_log(f"{error_message}", "ERROR")
