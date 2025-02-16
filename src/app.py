import utils.config as config
from flask import Flask, request, send_file, render_template
from models.report_generator import ReportGenerator
from utils.file_manager import FileManager
from werkzeug.datastructures import FileStorage
from utils.preprocess_csv import preprocess_csv  # Import the pre-processing function

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
    error_message = None
    if request.method == 'POST':
        try:
            # File check
            if 'file' not in request.files:
                raise ValueError('Dosya yüklenemedi')

            file = request.files['file']
            if file.filename == '':
                raise ValueError('Dosya seçilmedi')

            # Save as temporary file
            file.save(config.TEMP_PATH)

            # Pre-process the CSV file to add missing commas
            preprocess_csv(config.TEMP_PATH, config.TEMP_PATH, 17)

            generator = ReportGenerator(config.TEMP_PATH, config.REPORT_PATH)
            processed_data, summary = generator.generate_report()

            if processed_data is None:
                raise ValueError('Dosya işlenemedi')

        except Exception as e:
            error_message = str(e)

    return render_template('index.html', summary=summary, error_message=error_message)


@app.route('/download')
def download_csv():
    return send_file(config.REPORT_PATH,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=config.REPORT_NAME)


if __name__ == '__main__':
    # app.run(debug=True)
    # Simulate file upload
    with open('sample_ibkr_detailed_report.csv', 'rb') as f:
        file = FileStorage(f)
        temp_path = file_manager.create_file(config.TEMP_PATH)
        file.save(temp_path)

        # Pre-process the CSV file to add missing commas
        preprocess_csv(temp_path, temp_path, 17)

        generator = ReportGenerator(temp_path, config.REPORT_PATH)
        processed_data, summary = generator.generate_report()
        print(summary)
