import csv
from flask import Flask, request, send_file, render_template
import io
import os
import pandas as pd


# Flask uygulaması
app = Flask(__name__, template_folder='../templates')


# Anasayfa
@app.route('/')
def welcome():
    return render_template('index.html')


def read_and_process_tax_calculation(file_path):
    # Önceki Python kodundaki hesaplama fonksiyonu aynı kalacak
    df = pd.read_csv(file_path, header=0)

    def parse_numeric(value):
        try:
            if pd.isna(value):
                return 0
            value_str = str(value).replace(',', '').replace('(', '-').replace(')', '')
            return float(value_str)
        except ValueError:
            return 0  # Return 0 for non-numeric values

    processed_data = []
    tax_rate = 0.15

    for _, row in df.iterrows():
        quantity = parse_numeric(row['Quantity'])
        trade_price = parse_numeric(row['T. Price'])
        proceeds = parse_numeric(row['Proceeds'])
        basis = parse_numeric(row['Basis'])
        realized_pl = parse_numeric(row['Realized P/L'])

        taxable_profit = max(realized_pl, 0)
        tax_amount = taxable_profit * tax_rate
        net_profit = realized_pl - tax_amount

        processed_row = {
            'Symbol': row['Symbol'],
            'Date': row['Date/Time'],
            'Quantity': f"{quantity:.2f}",
            'TradePrice': f"{trade_price:.2f}",
            'Proceeds': f"{proceeds:.2f}",
            'Basis': f"{basis:.2f}",
            'RealizedProfit': f"{realized_pl:.2f}",
            'TaxableProfit': f"{taxable_profit:.2f}",
            'TaxRate': f"%{tax_rate * 100:.2f}",
            'TaxAmount': f"{tax_amount:.2f}",
            'NetProfit': f"{net_profit:.2f}"
        }
        processed_data.append(processed_row)

    summary = {
        'TotalTaxableProfit': f"{sum(float(row['TaxableProfit']) for row in processed_data):.2f}",
        'TotalTaxAmount': f"{sum(float(row['TaxAmount']) for row in processed_data):.2f}",
        'TotalNetProfit': f"{sum(float(row['NetProfit']) for row in processed_data):.2f}"
    }

    return processed_data, summary


@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST':
        # Dosya kontrolü
        if 'file' not in request.files:
            return 'Dosya yüklenemedi', 400

        file = request.files['file']

        # Geçici dosya olarak kaydet
        temp_path = 'temp_uploaded_file.csv'
        file.save(temp_path)

        try:
            # Vergi hesaplamasını yap
            processed_data, summary = read_and_process_tax_calculation(temp_path)

            # CSV dosyası oluştur
            output = io.StringIO()
            csv_writer = csv.DictWriter(output, fieldnames=processed_data[0].keys())

            # Başlıkları yaz
            csv_writer.writeheader()

            # Verileri yaz
            for row in processed_data:
                csv_writer.writerow(row)

            # İmleç başına dön
            output.seek(0)

            # Dosyayı geçici olarak kaydet
            with open('src/vergi_hesaplama_raporu.csv', 'w', newline='', encoding='utf-8') as f:
                f.write(output.getvalue())

        except Exception as e:
            return f'Hata: {str(e)}', 500
        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return render_template('index.html', summary=summary)


@app.route('/download')
def download_csv():
    return send_file('vergi_hesaplama_raporu.csv',
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='vergi_hesaplama_raporu.csv')


def analyze_csv_structure(file_path):
    df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')

    print("\nCSV Yapı Analizi:")
    print("=" * 50)

    for idx, row in df.iterrows():
        row_type = ""

        # İlk sütuna göre satır tipini belirle
    for idx, row in df.iterrows():
        # Use iloc for positional indexing
        if row.iloc[0] == 'Statement':
            if row.iloc[1] == 'Header':
                print(f"Row {idx}: Statement Header")
            elif row.iloc[1] == 'Data':
                print(f"Row {idx}: Statement Data - {row.iloc[2]}: {row.iloc[3]}")

        elif row.iloc[0] == 'Account Information':
            print(f"Row {idx}: Account Info - {row.iloc[2]}: {row.iloc[3]}")

        elif 'Trades' in str(row.values):
            print(f"Row {idx}: Trades section start")

        elif pd.isna(row.iloc[0]):
            print(f"Row {idx}: Empty row")

        else:
            print(f"Row {idx}: Other type - {row.iloc[0]}")

        print(f"Satır {idx+1}: {row_type}")
        print(f"İçerik: {', '.join(str(x) for x in row.values if pd.notna(x))}")
        print("-" * 50)


if __name__ == '__main__':
    analyze_csv_structure('U7470952_20241202_20250103.csv')
