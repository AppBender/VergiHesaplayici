from typing import List, Any
from decimal import Decimal
import csv
from protocols.report_writer_protocol import ReportWriterProtocol


class CSVReportWriter(ReportWriterProtocol):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file = open(file_path, 'w', newline='', encoding='utf-8-sig')
        self.csv_writer = csv.writer(self.file, delimiter=';', lineterminator='\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def write_header(self) -> None:
        # for now, we don't need to write a main header
        pass

    def write_section(self, section_name: str, data: List[Any]) -> None:
        if not data:
            return

        self.csv_writer.writerow([])  # Empty row

        # Special header for Trade section
        if section_name == "Trades":
            self.csv_writer.writerow([
                "İşlem Tipi",
                "Sembol",
                "Alış Tarihi",
                "Satış Tarihi",
                "İşlem Açıklaması",
                "Miktar",
                "Gerçekleşen K/Z (USD)",
                "Alış Fiyatı",
                "Satış Fiyatı",
                "Alış Kuru",
                "Satış Kuru",
                "Alış TL Değeri",
                "Satış TL Değeri",
                "TL Kar/Zarar",
                "Kategori"
            ])
        else:
            # Write headers for other sections
            self.csv_writer.writerow(self._get_section_headers(section_name))

        # Write section data
        for item in data:
            self.csv_writer.writerow(item.to_csv_row())

    def _get_section_headers(self, section_name: str) -> List[str]:
        base_headers = [
            "İşlem Tipi",
            "Sembol",
            "Tarih",
            "Satış Tarihi",
            "Açıklama",
            "Miktar",
            "USD",
            "Kur",
            "TL",
            "Kategori"
        ]

        if section_name == "Trades":
            return base_headers
        elif section_name in ["Dividends", "Withholding Tax", "Fees"]:
            # Filter out unwanted headers and add empty cells
            filtered_headers = [
                "İşlem Tipi",
                "Sembol",
                "Tarih",
                "",  # Empty cell
                "Açıklama",
                "",  # Empty cell
                "USD",
                "Kur",
                "TL",
                "Kategori"
            ]
            return filtered_headers

        return base_headers

    def write_summary(self, totals: dict[str, dict[str, Decimal]]) -> None:
        self.csv_writer.writerow([])  # Empty row
        self.csv_writer.writerow(["Özet"])
        self.csv_writer.writerow(["Kategori", "USD", "TL"])

        # Write category totals
        for category, amounts in totals.items():
            self.csv_writer.writerow([
                category,
                f"{amounts['USD']:.2f}",          # 2 decimals for USD
                f"{amounts['TL']:.2f}"            # 2 decimals for TL
            ])

        # Calculate grand totals
        total_usd = sum(amounts['USD'] for amounts in totals.values())
        total_try = sum(amounts['TL'] for amounts in totals.values())

        self.csv_writer.writerow([])  # Empty row
        self.csv_writer.writerow([
            "Toplam Kar/Zarar",
            f"{total_usd:.2f}",                   # 2 decimals for totals
            f"{total_try:.2f}"
        ])
