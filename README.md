# Vergi Hesaplayıcı (Tax Calculator)

A web application that processes Interactive Brokers (IBKR) activity reports and generates tax reports for Turkish investors.

## Features
- Process IBKR activity reports (CSV format)
- Support for multiple transaction types:
  * Stock trades
  * Options trades
  * Dividends
  * Withholding taxes
  * Exchange fees
- Automatic TCMB exchange rate conversion
- Tax report generation (CSV format)
- Detailed error logging

## Architecture
The project follows Clean Architecture and Domain-Driven Design principles:

```plaintext
src/
├── models/          # Domain models
│   └── domains/     # Trade, Dividend, Fee, etc.
├── protocols/       # Interface definitions
├── services/       # Application services
├── parsers/        # CSV data parsers
├── writers/        # Report generators
├── utils/          # Helper functions
└── app.py         # Web interface
```

## Project Structure
```plaintext
src/
├── models/          # Domain models
│   └── domains/     # Trade, Dividend, Fee, etc.
├── protocols/       # Interface definitions
├── services/       # Application services
├── parsers/        # CSV data parsers
├── writers/        # Report generators
├── utils/          # Helper functions
└── app.py         # Web interface

output/             # Generated reports and logs
    └── .gitkeep   # Keeps empty directory in git
temp/               # Temporary upload files
    └── .gitkeep   # Keeps empty directory in git
```

## Technologies
- Python 3.x
- Flask (Web framework)
- Pandas (Data processing)
- Clean Architecture & DDD

## Prerequisites
- Python 3.8 or higher
- pip package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/VergiHesaplayici.git
cd VergiHesaplayici

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the application
python src/app.py

# Visit http://localhost:5000 in your browser
```

## Configuration
The project uses a configuration file at `src/utils/config.py` which manages all path-related settings:

```python
from pathlib import Path

# Get the root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define paths
OUTPUT_DIR = BASE_DIR / 'output'
TEMP_PATH = BASE_DIR / 'temp_uploaded_file.csv'
REPORT_PATH = OUTPUT_DIR / 'vergi_hesaplama_raporu.csv'
REPORT_NAME = 'vergi_hesaplama_raporu.csv'
```

Create required directories:
```bash
mkdir -p temp output
touch output/.gitkeep
```

## File Handling
- Uploaded files are temporarily stored in `output/`
- Generated reports are saved in `output/`
- Temporary files are automatically cleaned up after processing
- Logs are written to `output/logs.txt`

> **Note**:
> - The configuration uses Python's `pathlib` for cross-platform path handling
> - Never commit sample report files containing real data to version control
> - Required directories are created automatically if they don't exist
> - Temporary files are automatically cleaned up after processing
> - Directory structure is maintained using `.gitkeep` files

## Input Format
IBKR activity report sections:

```plaintext
Trades:
- Header,DataDiscriminator,Asset Category,Currency,Symbol,Date/Time,Quantity,T. Price,Proceeds,Comm/Fee,Basis,Realized P/L

Dividends:
- Header,Currency,Date,Description,Amount

Withholding Tax:
- Header,Currency,Date,Description,Amount,Code

Fees:
- Header,Subtitle,Currency,Date,Description,Amount
```

## Output Format
Generated CSV report columns:
- İşlem Tipi (Transaction Type)
- Sembol (Symbol)
- Alış Tarihi (Buy Date)
- Satış Tarihi (Sell Date)
- İşlem Açıklaması (Description)
- Miktar (Quantity)
- USD Tutar (USD Amount)
- TCMB Kuru (Exchange Rate)
- TL Karşılığı (TRY Amount)
- Kategori (Category)

## Development

```bash
# Set environment variables
export FLASK_ENV=development
export FLASK_APP=src/app.py

# Run with debug mode
flask run --debug

# Check logs
tail -f output/logs.txt
```

## Error Handling
- Transaction errors logged to `output/logs.txt`
- Graceful handling of malformed data
- Detailed error messages in logs

## Security and Data Protection

### Protected Files
- CSV files containing financial data
- Log files with transaction details
- Temporary upload files

### Git History Cleanup
If sensitive data is accidentally committed, follow these steps:

```bash
# Install git-filter-repo (if not installed)
brew install git-filter-repo

# Commit any pending changes
git add .
git commit -m "Clean up before history rewrite"

# Remove sensitive files from history
git filter-repo --invert-paths --path-glob '*.csv' --path-glob 'output/*' --force

# Reset remote connection
git remote add origin https://github.com/yourusername/VergiHesaplayici.git

# Force push changes
git push origin --force --all
```

> **Warning**: After using `git filter-repo`:
> - All collaborators must clone the repository again
> - Repository history will be rewritten
> - Previous commits will get new hashes

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
MIT License
````
