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

        self.csv_writer.writerow([])  # Empty row for spacing
        headers = self._get_section_headers(section_name)
        self.csv_writer.writerow(headers)

        # Write data rows
        for item in data:
            self.csv_writer.writerow(item.to_csv_row())

        # Add section total for all sections
        if data:
            # Find indices for USD and TL columns
            usd_index = headers.index("USD") if "USD" in headers else headers.index("USD K/Z")
            tl_index = headers.index("TL") if "TL" in headers else headers.index("TL K/Z")

            # Calculate totals
            total_tl = sum(item.amount_tl for item in data if item.amount_tl)
            total_usd = sum(item.amount_usd for item in data if item.amount_usd)

            # Add taxable amount for Trades section
            if section_name == "Trades":
                taxable_index = headers.index("Vergiye Tabi Kazanç")
                total_taxable = sum(item.taxable_amount_tl for item in data if item.taxable_amount_tl)

            # Create total row with proper length
            total_row = [""] * len(headers)
            total_row[0] = "TOPLAM"

            if section_name == "Trades":
                total_row[taxable_index] = f"{total_taxable:.2f}"

            total_row[tl_index] = f"{total_tl:.2f}"
            total_row[usd_index] = f"{total_usd:.2f}"

            self.csv_writer.writerow(total_row)

    def _get_section_headers(self, section_name: str) -> List[str]:
        if section_name == "Trades":
            return [
                "İşlem Tipi",
                "Sembol",
                "İşlem Açıklaması",
                "Miktar",
                "Alış Tarihi",
                "Alış Fiyatı USD",
                "Alış Kuru",
                "Satış Tarihi",
                "Satış Fiyatı USD",
                "Satış Kuru",
                "Komisyon TL",
                "Alış TL Değeri",
                "Satış TL Değeri",
                "Yİ-ÜFE Artış (%)",
                "Endekslenmiş Alış Değeri",
                "Vergiye Tabi Kazanç",
                "TL K/Z",
                "USD K/Z",
                "Kategori"
            ]
        else:
            return [
                "İşlem Tipi",
                "Sembol",
                "Açıklama",
                "Tarih",
                "USD",
                "Kur",
                "TL",
                "Kategori"
            ]

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
