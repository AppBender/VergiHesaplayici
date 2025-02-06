import utils.config as config

from flask import Flask, request, send_file, render_template
from models.csv_processor import CSVProcessor
from utils.file_manager import FileManager
from werkzeug.datastructures import FileStorage


app = Flask(__name__, template_folder='templates/')
file_manager = FileManager()
file_manager.clear_directory(config.OUTPUT_DIR)


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
        # File check
        if 'file' not in request.files:
            return 'Dosya yüklenemedi', 400

        file = request.files['file']
        if file.filename == '':
            return 'Dosya seçilmedi', 400

        # Save as temporary file
        file.save(config.TEMP_PATH)

        processor = CSVProcessor(config.TEMP_PATH, config.REPORT_PATH)
        processed_data, summary = processor.process_csv()

        if processed_data is None:
            return 'Hata: Dosya işlenemedi', 500

    return render_template('index.html', summary=summary)


@app.route('/download')
def download_csv():
    return send_file(config.REPORT_PATH,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=config.REPORT_NAME)


if __name__ == '__main__':
    # app.run(debug=True)
    # Simulate file upload
    with open('U7470952_20241202_20250103.csv', 'rb') as f:
        file = FileStorage(f)
        temp_path = file_manager.create_file(config.TEMP_PATH)
        file.save(temp_path)

        processor = CSVProcessor(temp_path, config.REPORT_PATH)
        processed_data, summary = processor.process_csv()
        print(summary)
