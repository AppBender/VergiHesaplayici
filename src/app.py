# Service and writer imports
from services.report_service import ReportService
from writers.csv_report_writer import CSVReportWriter

# Standard library imports
from flask import Flask, request, send_file, render_template
from pathlib import Path
from utils.config import OUTPUT_DIR
from werkzeug.datastructures import FileStorage

# Local imports
import utils.config as config
from utils.file_manager import FileManager

# Parser imports
from parsers.dividend_parser import DividendParser
from parsers.fee_parser import FeeParser
from parsers.trade_parser import TradeParser
from parsers.withholding_tax_parser import WithholdingTaxParser


app = Flask(__name__, template_folder='templates/')
file_manager = FileManager()
file_manager.clear_directory(config.OUTPUT_DIR)


def initialize_parsers():
    return [
        TradeParser(),
        FeeParser(),
        DividendParser(),
        WithholdingTaxParser(),
    ]


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
            temp_path = file_manager.create_file(config.TEMP_PATH)
            file.save(temp_path)

            # Create report service
            writer = CSVReportWriter(config.REPORT_PATH)
            service = ReportService(initialize_parsers(), writer)

            # Process report and get summary
            try:
                summary = service.process_report(temp_path)
            except Exception as e:
                raise ValueError('Rapor işlenemedi') from e

        except Exception as e:
            error_message = str(e)

    return render_template('index.html', summary=summary, error_message=error_message)


@app.route('/download')
def download_csv():
    return send_file(config.REPORT_PATH,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=config.REPORT_NAME)


def create_required_directories():
    # Create output directory only
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    (output_dir / '.gitkeep').touch()


if __name__ == '__main__':
    # Create required directories first
    create_required_directories()

    # Run the Flask app
    app.run(debug=True)

    # simualte_file_upload()

    # Simulate file upload
    def simualte_file_upload():
        with open('sample/sample_ibkr_detailed_report.csv', 'rb') as f:
            file = FileStorage(f)
            temp_path = file_manager.create_file(config.TEMP_PATH)
            file.save(temp_path)

            # Create report service
            writer = CSVReportWriter(config.REPORT_PATH)
            service = ReportService(initialize_parsers(), writer)

            # Process report
            if not service.process_report(temp_path):
                print("Error: Report could not be processed")
            else:
                print("Report created successfully")
                print(f"Report file: {config.REPORT_PATH}")
