from typing import Protocol


# Define the Database Protocol
class Database(Protocol):
    def log_info(self):
        pass

    def log_error(self):
        pass
