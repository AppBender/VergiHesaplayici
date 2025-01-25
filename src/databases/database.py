from typing import Protocol


# Define the Database Protocol
class Database(Protocol):
    def log_request(self):
        pass

    def log_response(self):
        pass

    def log_error(self):
        pass
