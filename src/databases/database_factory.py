from databases.file_db import FileDB
from databases.mongo_db import MongoDB


class DatabaseFactory:
    @staticmethod
    def get_database(name: str):
        if name == "mongoDB":
            return MongoDB()
        elif name == "fileDB":
            return FileDB()
        else:
            raise ValueError(f"Unknown database: {name}")
