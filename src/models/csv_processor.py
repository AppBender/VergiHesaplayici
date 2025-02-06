import csv
import io
import os
from datetime import datetime

from models.csv_parser import CSVParser
from utils.exchange_rate import get_exchange_rate


class CSVProcessor:
    def __init__(self, temp_path, report_path):
        self.temp_path = temp_path
        self.report_path = report_path

    def process_csv(self):
        try:
            parser = CSVParser(self.temp_path)

            # Vergi hesaplamasını yap
            processed_data, summary, fieldnames = parser.parse()

            # Group data by categories
            categories = {
                'Hisse Senedi': [],
                'Opsiyon': [],
                'Temettü': [],
                'Stopaj': []
            }

            for row in processed_data:
                if row['Type'] == 'Trade':
                    if row['Asset Category'] == 'Equity and Index Options':
                        categories['Opsiyon'].append(row)
                    else:
                        categories['Hisse Senedi'].append(row)
                elif row['Type'] == 'Dividend':
                    categories['Temettü'].append(row)
                elif row['Type'] == 'Withholding Tax':
                    categories['Stopaj'].append(row)
                elif row['Type'] == 'Fee':
                    categories['Stopaj'].append(row)

            # Calculate totals for each category
            totals = {
                'Hisse Senedi': {'USD': 0, 'TL': 0},
                'Opsiyon': {'USD': 0, 'TL': 0},
                'Temettü': {'USD': 0, 'TL': 0},
                'Stopaj': {'USD': 0, 'TL': 0}
            }

            for category, rows in categories.items():
                for row in rows:
                    if 'RealizedProfit' in row:
                        totals[category]['USD'] += float(row['RealizedProfit'])
                    if 'Amount' in row:
                        totals[category]['USD'] += float(row['Amount'])

            # CSV dosyası oluştur
            output = io.StringIO()
            csv_writer = csv.writer(output)

            # Write headers
            csv_writer.writerow(['İşlem Tipi', 'Sembol', 'Tarih', 'İşlem Açıklaması', 'USD Tutar', 'TCMB Kuru', 'TL Karşılığı', 'Kategori'])

            # Write data
            previous_row_empty = False
            for category, rows in categories.items():
                for row in rows:
                    date_str = str(row['Date/Time']).split(',')[0]  # Ensure date_str is a string
                    if date_str.lower() == 'nan':
                        continue  # Skip rows with NaN date

                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    exchange_rate = get_exchange_rate(date_obj)
                    tl_equivalent = float(row['RealizedProfit']) * exchange_rate if 'RealizedProfit' in row else float(row['Amount']) * exchange_rate

                    if category == 'Hisse Senedi':
                        csv_writer.writerow([
                            'Hisse Senedi', row['Symbol'], row['Date/Time'], 'Satış Karı' if float(row['RealizedProfit']) > 0 else 'Satış Zararı',
                            row['RealizedProfit'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Alım-Satım'
                        ])
                    elif category == 'Opsiyon':
                        csv_writer.writerow([
                            'Opsiyon', row['Symbol'], row['Date/Time'], 'Opsiyon Karı' if float(row['RealizedProfit']) > 0 else 'Opsiyon Zararı',
                            row['RealizedProfit'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Alım-Satım'
                        ])
                    elif category == 'Temettü':
                        csv_writer.writerow([
                            'Temettü', row['Symbol'], row['Date/Time'], 'Brüt Temettü',
                            row['Amount'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Temettü'
                        ])
                    elif category == 'Stopaj':
                        csv_writer.writerow([
                            'Stopaj', row['Symbol'], row['Date/Time'], 'Temettü Stopajı',
                            row['Amount'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Stopaj'
                        ])
                    previous_row_empty = False
                # Add an empty row between sections if the previous row is not empty
                if not previous_row_empty:
                    csv_writer.writerow(['', '', '', '', '', '', '', ''])
                    previous_row_empty = True

            # Write totals
            csv_writer.writerow(['Özet Hesaplama', '', '', '', '', '', '', ''])
            csv_writer.writerow(['Kategori', 'USD Toplam', 'TL Toplam', '', '', '', '', ''])
            for category, total in totals.items():
                csv_writer.writerow([category, total['USD'], total['TL'], '', '', '', '', ''])

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
