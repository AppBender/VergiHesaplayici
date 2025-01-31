import csv
from flask import Flask, request, send_file, render_template
import io
import os
import pandas as pd
from databases.file_db import FileDB

from models.csv_parser import CSVParser


# Flask uygulaması
app = Flask(__name__, template_folder='../templates')
db = FileDB()
db.clear_logs()
report_file_path = 'src/vergi_hesaplama_raporu.csv'


# Anasayfa
@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/calculate-tax', methods=['POST'])
def process_tax_route():
    """Processes tax calculation route for uploaded CSV files.

    This function handles the file upload process, validates the uploaded file,
    processes the tax calculations using CSVParser, and generates both a downloadable
    CSV report and an HTML results page.

    Returns:
        tuple: A tuple containing either:
            - (str, int): Error message and HTTP status code (400 or 500) if an error
            occurs
            - template: Rendered 'results.html' template with processed data and summary
            if successful

    Raises:
        Exception: Any exception that occurs during file processing or tax calculation

    Notes:
        - Expects a CSV file upload through POST request
        - Saves processed results to 'src/vergi_hesaplama_raporu.csv'
        - Uses temporary file 'temp_uploaded_file.csv' during processing
    """
    if 'file' not in request.files:
        return 'Dosya yüklenmedi', 400

    file = request.files['file']
    if file.filename == '':
        return 'Dosya seçilmedi', 400

    try:
        temp_path = 'temp_uploaded_file.csv'
        file.save(temp_path)

        parser = CSVParser(temp_path)
        processed_data, summary, fieldnames = parser.parse()

        output = io.StringIO()
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames)

        csv_writer.writeheader()
        for row in processed_data:
            csv_writer.writerow(row)

        output.seek(0)

        with open(report_file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())

        return render_template('results.html', results=processed_data, summary=summary)

    except Exception as e:
        print(f'Hata: {str(e)}')
        return f'Hata: {str(e)}', 500


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Process uploaded CSV file for tax calculations and generate report.

    This function handles both GET and POST requests:
    - GET: Renders the index template
    - POST: Processes uploaded CSV file, calculates taxes, and generates report

    The function performs the following steps on POST:
    1. Validates file upload
    2. Saves uploaded file temporarily
    3. Parses CSV data and calculates taxes
    4. Generates output CSV with tax calculations
    5. Saves report file
    6. Cleans up temporary file

    Returns:
        On GET: Rendered index.html template
        On POST success: Rendered index.html template with calculation summary
        On POST error: Error message with appropriate HTTP status code (400 or 500)

    Raises:
        Exception: If any error occurs during file processing or tax calculations
    """
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
            parser = CSVParser(temp_path)

            # Vergi hesaplamasını yap
            processed_data, summary, fieldnames = parser.parse()

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
            with open(report_file_path, 'w', newline='', encoding='utf-8') as f:
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
    app.run(debug=True)
    # analyze_csv_structure('U7470952_20241202_20250103.csv')
    # processed_data, summary, fieldnames = calculate_tax('U7470952_20241202_20250103.csv')    # print(processed_data)
    # print(summary)
