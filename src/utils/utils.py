from databases.file_db import FileDB
import pandas as pd


def log(message: str):
    """
    A global log function to replace print.
    """
    print(f"[LOG] {message}")


def parse_numeric(value):
    db = FileDB()

    try:
        if pd.isna(value):
            return 0
        value_str = str(value).replace(',', '').replace('(', '-').replace(')', '')
        return float(value_str)
    except ValueError as e:
        db.log_error(f"ValueError: {str(e)} for value: {value}")
        # print(f"ValueError: {str(e)} for value: {value}")
        return 0  # Return 0 for non-numeric values
