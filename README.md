# Tax Calculator for IBKR Reports

A web application that processes Interactive Brokers (IBKR) activity reports and generates tax reports for Turkish investors.

## Features
- Process IBKR activity reports (CSV format)
- Support for transaction types:
  * Stock trades
  * Options trades
  * Dividends
  * Withholding taxes
- Automatic TCMB (Turkish Central Bank) exchange rate conversion
- Tax report generation (CSV format)
- YI-ÜFE (Producer Price Index) adjustment for long-term holdings
- Detailed error logging

## Architecture
The project follows Clean Architecture and Domain-Driven Design principles:

```plaintext
src/
├── models/          # Domain models
│   └── domains/     # Trade, Dividend, Fee, etc.
├── protocols/       # Interface definitions
├── services/        # Application services
├── parsers/         # CSV data parsers
├── writers/         # Report generators
├── utils/           # Helper functions
└── app.py           # Web interface
```

## Prerequisites
- Python 3.8 or higher
- TCMB EVDS API key (for exchange rates)
- pip package manager

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd TaxCalculator

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export TCMB_API_KEY=your_api_key
```

## Usage

```bash
# Start the application
python src/app.py

# Visit http://localhost:5000 in your browser
```

## Input Format
The application expects IBKR activity reports in CSV format with the following sections:

### Trades Section
- Contains stock and options trades
- Required columns:
  * Header
  * DataDiscriminator
  * Asset Category
  * Currency
  * Symbol
  * Date/Time
  * Quantity
  * T. Price
  * Proceeds
  * Comm/Fee
  * Basis
  * Realized P/L

### Dividends Section
- Contains dividend payments
- Required columns:
  * Header
  * Currency
  * Date
  * Description
  * Amount

### Withholding Tax Section
- Contains tax withholdings
- Required columns:
  * Header
  * Currency
  * Date
  * Description
  * Amount
  * Code

## Output Format
The generated tax report (CSV) includes:

### Stock and Option Trades
- Trade Type (İşlem Tipi)
- Symbol (Sembol)
- Trade Description (İşlem Açıklaması)
- Quantity (Miktar)
- Buy Date (Alış Tarihi)
- Buy Price USD (Alış Fiyatı USD)
- Buy Exchange Rate (Alış Kuru)
- Sell Date (Satış Tarihi)
- Sell Price USD (Satış Fiyatı USD)
- Sell Exchange Rate (Satış Kuru)
- Commission TRY (Komisyon TL)
- Buy Amount TRY (Alış TL Değeri)
- Sell Amount TRY (Satış TL Değeri)
- YI-ÜFE Rate (YI-ÜFE Artış %)
- Indexed Buy Amount (Endekslenmiş Alış Değeri)
- Taxable Amount (Vergiye Tabi Kazanç)
- TRY P/L (TL K/Z)
- USD P/L (USD K/Z)
- Category (Kategori)

### Dividends and Withholding Tax
- Transaction Type (İşlem Tipi)
- Symbol (Sembol)
- Description (Açıklama)
- Date (Tarih)
- USD Amount (USD)
- Exchange Rate (Kur)
- TRY Amount (TL)
- Category (Kategori)

## Error Handling
- All errors are logged to `output/error.log`
- Warnings are logged to `output/warning.log`
- General information is logged to `output/info.log`

## File Structure
```plaintext
output/
├── logs/           # Log files
├── reports/        # Generated reports
└── .gitkeep       # Keeps empty directory in git
```

## Known Limitations
- Forex trades are currently not supported
- Only supports IBKR CSV report format
- Requires TCMB EVDS API access for exchange rates

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
MIT License