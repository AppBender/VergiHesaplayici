import csv
from flask import Flask, request, send_file, render_template
import io
import os
import pandas as pd
from databases.file_db import FileDB
from werkzeug.datastructures import FileStorage


# Flask uygulaması
app = Flask(__name__, template_folder='../templates')
db = FileDB()
db.clear_logs()


# Anasayfa
@app.route('/')
def welcome():
    return render_template('index.html')


def parse_numeric(value):
    try:
        if pd.isna(value):
            return 0
        value_str = str(value).replace(',', '').replace('(', '-').replace(')', '')
        return float(value_str)
    except ValueError as e:
        db.log_error(f"ValueError: {str(e)} for value: {value}")
        # print(f"ValueError: {str(e)} for value: {value}")
        return 0  # Return 0 for non-numeric values


def calculate_tax(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')

    processed_data = []
    tax_rate = 0.15
    total_taxable_profit = 0
    total_tax_amount = 0
    total_net_profit = 0

    for idx, row in df.iterrows():
        try:
            if row.iloc[0] == 'Statement' and row.iloc[1] == 'Data':
                if row.iloc[2] == 'Realized P/L':
                    realized_pl = parse_numeric(row.iloc[3])
                    taxable_profit = max(realized_pl, 0)
                    tax_amount = taxable_profit * tax_rate
                    net_profit = realized_pl - tax_amount

                    total_taxable_profit += taxable_profit
                    total_tax_amount += tax_amount
                    total_net_profit += net_profit

                    processed_row = {
                        'Type': 'Statement',
                        'Description': row.iloc[2],
                        'RealizedProfit': f"{realized_pl:.2f}",
                        'TaxableProfit': f"{taxable_profit:.2f}",
                        'TaxAmount': f"{tax_amount:.2f}",
                        'NetProfit': f"{net_profit:.2f}"
                    }
                    processed_data.append(processed_row)

            elif row.iloc[0] == 'Account Information' and row.iloc[1] == 'Data':
                processed_row = {
                    'Type': 'Account Information',
                    'Field': row.iloc[2],
                    'Value': row.iloc[3]
                }
                processed_data.append(processed_row)

            elif row.iloc[0] == 'Trades' and row.iloc[1] == 'Data':
                try:
                    quantity = parse_numeric(row.iloc[2])
                    trade_price = parse_numeric(row.iloc[3])
                    proceeds = parse_numeric(row.iloc[4])
                    commission = parse_numeric(row.iloc[5])
                    realized_pl = parse_numeric(row.iloc[6])

                    taxable_profit = max(realized_pl, 0)
                    tax_amount = taxable_profit * tax_rate
                    net_profit = realized_pl - tax_amount

                    total_taxable_profit += taxable_profit
                    total_tax_amount += tax_amount
                    total_net_profit += net_profit

                    processed_row = {
                        'Type': 'Trade',
                        'Symbol': row.iloc[1],
                        'Quantity': f"{quantity:.2f}",
                        'TradePrice': f"{trade_price:.2f}",
                        'Proceeds': f"{proceeds:.2f}",
                        'Commission': f"{commission:.2f}",
                        'RealizedProfit': f"{realized_pl:.2f}",
                        'TaxableProfit': f"{taxable_profit:.2f}",
                        'TaxAmount': f"{tax_amount:.2f}",
                        'NetProfit': f"{net_profit:.2f}"
                    }
                    processed_data.append(processed_row)
                except ValueError as e:
                    db.log_error(f"ValueError: {str(e)} for row {idx}")

            elif row.iloc[0] == 'Fees' and row.iloc[1] == 'Data':
                fee_amount = parse_numeric(row.iloc[2])
                processed_row = {
                    'Type': 'Fee',
                    'Description': row.iloc[1],
                    'Amount': f"{fee_amount:.2f}"
                }
                processed_data.append(processed_row)

            elif row.iloc[0] == 'Dividends' and row.iloc[1] == 'Data':
                dividend_amount = parse_numeric(row.iloc[2])
                processed_row = {
                    'Type': 'Dividend',
                    'Description': row.iloc[1],
                    'Amount': f"{dividend_amount:.2f}"
                }
                processed_data.append(processed_row)

            elif row.iloc[0] == 'Withholding Tax' and row.iloc[1] == 'Data':
                withholding_tax_amount = parse_numeric(row.iloc[2])
                processed_row = {
                    'Type': 'Withholding Tax',
                    'Description': row.iloc[1],
                    'Amount': f"{withholding_tax_amount:.2f}"
                }
                processed_data.append(processed_row)
        except Exception as e:
            db.log_error(f"Error processing row {idx}: {str(e)}")

    # Dynamically generate fieldnames from processed data
    fieldnames = set()
    for row in processed_data:
        fieldnames.update(row.keys())
    fieldnames = list(fieldnames)

    summary = {
        'TotalTaxableProfit': f"{total_taxable_profit:.2f}",
        'TotalTaxAmount': f"{total_tax_amount:.2f}",
        'TotalNetProfit': f"{total_net_profit:.2f}"
    }

    return processed_data, summary, fieldnames

# Usage in the route
@app.route('/calculate-tax', methods=['POST'])
def process_tax_route():
    if 'file' not in request.files:
        return 'Dosya yüklenmedi', 400

    file = request.files['file']
    if file.filename == '':
        return 'Dosya seçilmedi', 400

    try:
        temp_path = 'temp_uploaded_file.csv'
        file.save(temp_path)

        processed_data, summary, fieldnames = calculate_tax(temp_path)

        output = io.StringIO()
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames)

        csv_writer.writeheader()
        for row in processed_data:
            csv_writer.writerow(row)

        output.seek(0)

        with open('src/vergi_hesaplama_raporu.csv', 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())

        return render_template('results.html', results=processed_data, summary=summary)

    except Exception as e:
        print(f'Hata: {str(e)}')
        return f'Hata: {str(e)}', 500


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
            processed_data, summary, fieldnames = calculate_tax(temp_path)

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
            with open('src/vergi_hesaplama_raporu.csv', 'w', newline='', encoding='utf-8') as f:
                f.write(output.getvalue())

        except Exception as e:
            print(f'Hata: {str(e)}')
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
    df = pd.read_csv(file_path, encoding='utf-8', header=None)

    # db.log_info("CSV Yapı Analizi:")
    # db.log_info("=" * 50)

    # İlk sütuna göre satır tipini belirle
    for idx, row in df.iterrows():
        row_section = row.iloc[0]
        row_type = row.iloc[1]

        # Use iloc for positional indexing
        if row.iloc[0] == 'Statement':
            if row.iloc[1] == 'Header':
                db.log_info(f"Index {idx}: Statement Header")
            elif row.iloc[1] == 'Data':
                db.log_info(f"Index {idx}: Statement Data - {row.iloc[2]}: {row.iloc[3]}")

        elif row.iloc[0] == 'Account Information':
            db.log_info(f"Index {idx}: Account Info - {row.iloc[2]}: {row.iloc[3]}")

        elif row.iloc[0] == 'Trades':
            db.log_info(f"Index {idx}: Trades")

        elif row.iloc[0] == 'Fees':
            db.log_info(f"Index {idx}: Fees")

        elif row.iloc[0] == 'Dividends':
            db.log_info(f"Index {idx}: Dividends")

        elif row.iloc[0] == 'Withholding Tax':
            db.log_info(f"Index {idx}: Withholding Tax")

        elif pd.isna(row.iloc[0]):
            db.log_info(f"Index {idx}: Empty row")

        else:
            db.log_info(f"Index {idx}: Other type - {row.iloc[0]}")

        db.log_info(f"Row {idx+1}: Section: {row_section}, Type: {row_type}")
        db.log_info(f"Content: {', '.join(str(x) for x in row.values if pd.notna(x))}")
        db.log_info("-" * 50)


if __name__ == '__main__':
    # app.run(debug=True)
    # analyze_csv_structure('U7470952_20241202_20250103.csv')
    processed_data, summary, fieldnames = calculate_tax('U7470952_20241202_20250103.csv')    # print(processed_data)
    print(summary)
