import csv
import io
import os
import pandas as pd

from models.csv_processor import CSVProcessor
from flask import Flask, request, send_file, render_template
from databases.file_db import FileDB
from models.csv_parser import CSVParser


# Flask uygulaması
app = Flask(__name__, template_folder='../templates')
db = FileDB()
db.clear_logs()

report_name = "vergi_hesaplama_raporu.csv"
report_path = f'src/{report_name}'


# Anasayfa
@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Flask route handler for the index page that processes uploaded CSV files.

    This function handles both GET and POST requests. For POST requests, it processes
    an uploaded CSV file and generates a summary report. For GET requests, it simply
    renders the index template.

    Returns:
        For GET requests:
            render_template: Renders 'index.html' with no summary data
        For POST requests:
            On success: render_template: Renders 'index.html' with processed summary data
            On file upload error: tuple: ('Dosya yüklenemedi', 400)
            On processing error: tuple: ('Hata: Dosya işlenemedi', 500)

    Raises:
        None: Exceptions are handled internally

    Note:
        The function expects a file to be uploaded with the form field name 'file'
        The uploaded file is temporarily saved as 'temp_uploaded_file.csv'
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

        processor = CSVProcessor(temp_path, report_path)
        processed_data, summary = processor.process_csv()

        if processed_data is None:
            return 'Hata: Dosya işlenemedi', 500

    return render_template('index.html', summary=summary)


@app.route('/download')
def download_csv():
    return send_file(report_name,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=report_name)


if __name__ == '__main__':
    app.run(debug=True)
    # processed_data, summary, fieldnames = calculate_tax('U7470952_20241202_20250103.csv')
    # print(processed_data)
    # print(summary)
