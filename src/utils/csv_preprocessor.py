import pandas as pd
import csv
from typing import List

class CSVPreprocessor:
    @staticmethod
    def preprocess(input_path: str, expected_columns: int = 17) -> pd.DataFrame:
        """
        CSV dosyasını işler ve tüm satırların beklenen sayıda sütuna sahip olmasını sağlar.

        Args:
            input_path: İşlenecek CSV dosyasının yolu
            expected_columns: Beklenen sütun sayısı (varsayılan: 17)

        Returns:
            pandas.DataFrame: İşlenmiş veri
        """
        # Önce raw data olarak oku
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
