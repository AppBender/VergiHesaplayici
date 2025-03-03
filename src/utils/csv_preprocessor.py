import pandas as pd
import csv
from typing import List


class CSVPreprocessor:
    @staticmethod
    def preprocess(input_path: str, expected_columns: int = 17) -> pd.DataFrame:
        """
        Processes the CSV file and ensures that all rows have the expected number of columns.

        Args:
            input_path: Path to the CSV file to be processed
            expected_columns: Expected number of columns (default: 17)

        Returns:
            pandas.DataFrame: Processed data
        """
        # First, read as raw data
        rows: List[List[str]] = []
        with open(input_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                # Satırı istenen uzunluğa getir
                if len(row) < expected_columns:
                    row.extend([''] * (expected_columns - len(row)))
                elif len(row) > expected_columns:
                    row = row[:expected_columns]
                rows.append(row)

        # DataFrame'e çevir
        return pd.DataFrame(rows)
