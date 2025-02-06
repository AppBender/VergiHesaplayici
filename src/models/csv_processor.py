import csv
import io
import os

from models.csv_parser import CSVParser


class CSVProcessor:
    def __init__(self, temp_path, report_path):
        self.temp_path = temp_path
        self.report_path = report_path

    def process_csv(self):
        try:
            parser = CSVParser(self.temp_path)

            # Vergi hesaplamasını yap
            processed_data, summary, fieldnames = parser.parse()

            # Desired order of columns
            order = [
                'Type', 'Symbol', 'Quantity', 'TradePrice', 'Proceeds', 'Commission',
                'RealizedProfit', 'TaxableProfit', 'TaxAmount', 'NetProfit',
                'Description', 'Amount'
            ]

            # Ensure fieldnames are in the desired order
            fieldnames = [field for field in order if field in fieldnames]

            # CSV dosyası oluştur
            output = io.StringIO()
            csv_writer = csv.DictWriter(output, fieldnames=fieldnames)

            # Başlıkları yaz
            csv_writer.writeheader()

            # Verileri yaz
            for row in processed_data:
                csv_writer.writerow(row)

            # İmleç başına dön
            output.seek(0)

            # Dosyayı geçici olarak kaydet
            with open(self.report_path, 'w', newline='', encoding='utf-8') as f:
                f.write(output.getvalue())

            return processed_data, summary

        except Exception as e:
            print(f'Hata: {str(e)}')
            return None, None
        finally:
            # Geçici dosyayı sil
            if os.path.exists(self.temp_path):
                os.remove(self.temp_path)
