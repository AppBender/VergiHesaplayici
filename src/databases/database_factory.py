from databases.mongo_db import MongoDB


class DatabaseFactory:
    @staticmethod
    def get_database(name: str):
        if name == "mongoDB":
            return MongoDB()
        else:
            raise ValueError(f"Unknown database: {name}")
