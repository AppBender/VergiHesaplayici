from typing import List, Any
from decimal import Decimal
import csv
from protocols.report_writer_protocol import ReportWriterProtocol


class CSVReportWriter(ReportWriterProtocol):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file = open(file_path, 'w', newline='', encoding='utf-8-sig')
        self.csv_writer = csv.writer(self.file, delimiter=';', lineterminator='\n')

    def write_header(self) -> None:
        self.csv_writer.writerow([
            'İşlem Tipi', 'Sembol', 'Alış Tarihi', 'Satış Tarihi',
            'İşlem Açıklaması', 'Miktar', 'USD Tutar', 'TCMB Kuru',
            'TL Karşılığı', 'Kategori'
        ])

    def write_section(self, section_name: str, rows: List[Any]) -> None:
        for row in rows:
            self.csv_writer.writerow(row.to_csv_row())
        self.csv_writer.writerow([''] * 10)  # Empty row between sections

    def write_summary(self, totals: dict[str, dict[str, Decimal]]) -> None:
        self.csv_writer.writerow(['Özet Hesaplama'] + [''] * 9)
        self.csv_writer.writerow(['Kategori', 'USD Toplam', 'TL Toplam'] + [''] * 7)

        total_usd = Decimal('0')
        total_tl = Decimal('0')

        for category, total in totals.items():
            total_usd += total['USD']
            total_tl += total['TL']
            self.csv_writer.writerow([
                category,
                f"{total['USD']:.2f}",
                f"{total['TL']:.2f}"
            ] + [''] * 7)

        self.csv_writer.writerow([
            'Toplam Kar/Zarar',
            f"{total_usd:.2f}",
            f"{total_tl:.2f}"
        ] + [''] * 7)

    def __del__(self):
        if hasattr(self, 'file'):
            self.file.close()
