from pathlib import Path

# Get the root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define paths
OUTPUT_DIR = BASE_DIR / 'output'
TEMP_PATH = BASE_DIR / 'temp_uploaded_file.csv'
REPORT_PATH = OUTPUT_DIR / 'vergi_hesaplama_raporu.csv'
REPORT_NAME = 'vergi_hesaplama_raporu.csv'
