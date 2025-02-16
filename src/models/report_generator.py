import csv
import io
import os
from datetime import datetime

from models.csv_parser import CSVParser
from utils.exchange_rate import get_exchange_rate


class ReportGenerator:
    def __init__(self, temp_path, report_path):
        self.temp_path = temp_path
        self.report_path = report_path

    def generate_report(self):
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

            # CSV dosyası oluştur
            output = io.StringIO()
            csv_writer = csv.writer(output, delimiter=';', lineterminator='\n')

            # Write headers
            csv_writer.writerow(['İşlem Tipi', 'Sembol', 'Alış Tarihi', 'Satış Tarihi', 'İşlem Açıklaması', 'Miktar', 'USD Tutar', 'TCMB Kuru', 'TL Karşılığı', 'Kategori'])

            # Write data
            previous_row_empty = False
            for category, rows in categories.items():
                for row in rows:
                    # Skip buy transactions
                    if 'RealizedProfit' in row and float(row['RealizedProfit']) == 0:
                        continue

                    if category in ['Hisse Senedi', 'Opsiyon']:
                        buy_date_str = str(row['Buy Date']).split(',')[0]  # Ensure buy_date_str is a string
                        sell_date_str = str(row['Sell Date']).split(',')[0]  # Ensure sell_date_str is a string

                        if buy_date_str.lower() == 'nan' or sell_date_str.lower() == 'nan':
                            continue  # Skip rows with NaN date

                        sell_date_obj = datetime.strptime(sell_date_str, '%Y-%m-%d')
                        exchange_rate = get_exchange_rate(sell_date_obj)
                        tl_equivalent = float(row['USD Amount']) * exchange_rate

                        # Accumulate totals
                        totals[category]['USD'] += float(row['USD Amount'])
                        totals[category]['TL'] += tl_equivalent

                        csv_writer.writerow([
                            'Hisse Senedi' if category == 'Hisse Senedi' else 'Opsiyon', row['Symbol'], buy_date_str, sell_date_str, row['Description'],
                            row['Quantity'], row['USD Amount'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Alım-Satım'
                        ])
                    else:
                        date_str = str(row['Date/Time']).split(',')[0]  # Ensure date_str is a string
                        if date_str.lower() == 'nan':
                            continue  # Skip rows with NaN date

                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        exchange_rate = get_exchange_rate(date_obj)
                        tl_equivalent = float(row['Amount']) * exchange_rate

                        # Accumulate totals
                        totals[category]['USD'] += float(row['Amount'])
                        totals[category]['TL'] += tl_equivalent

                        if category == 'Temettü':
                            csv_writer.writerow([
                                'Temettü', row['Symbol'], date_str, '', 'Brüt Temettü',
                                row['Amount'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Temettü', ''
                            ])
                        elif category == 'Stopaj':
                            csv_writer.writerow([
                                'Stopaj', row['Symbol'], date_str, '', 'Temettü Stopajı',
                                row['Amount'], f"{exchange_rate:.4f}", f"{tl_equivalent:.2f}", 'Stopaj', ''
                            ])
                    previous_row_empty = False
                # Add an empty row between sections if the previous row is not empty
                if not previous_row_empty:
                    csv_writer.writerow(['', '', '', '', '', '', '', '', '', ''])
                    previous_row_empty = True

            # Calculate total profit/loss
            total_profit_loss_tl = sum(total['TL'] for total in totals.values())
            total_profit_loss_usd = sum(total['USD'] for total in totals.values())

            # Write totals
            csv_writer.writerow(['Özet Hesaplama', '', '', '', '', '', '', '', '', ''])
            csv_writer.writerow(['Kategori', 'USD Toplam', 'TL Toplam', '', '', '', '', '', '', ''])
            for category, total in totals.items():
                csv_writer.writerow([category, total['USD'], total['TL'], '', '', '', '', '', '', ''])
            csv_writer.writerow(['Toplam Kar/Zarar', total_profit_loss_usd, total_profit_loss_tl, '', '', '', '', '', '', ''])

            # İmleç başına dön
            output.seek(0)

            # Dosyayı kaydet
            with open(self.report_path, 'w', newline='', encoding='utf-8-sig') as f:
                f.write('\ufeff')  # UTF-8 BOM
                f.write(output.getvalue())

            return processed_data, summary

        except Exception as e:
            print(f"Hata: {str(e)}")
            return None, None
        finally:
            # Geçici dosyayı sil
            if os.path.exists(self.temp_path):
                os.remove(self.temp_path)
