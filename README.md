# Vergi Hesaplayıcı (Tax Calculator)

A web application that calculates taxes on financial transactions by processing CSV files.

## Features
- CSV file upload and processing
- Tax calculation based on realized profits
- Downloadable tax report generation

## Technologies
- Python 3.x
- Flask
- Pandas
- HTML/CSS

## Installation
```bash
pip install -r requirements.txt
```

## Usage
1. Run the application:
```bash
python src/app.py
```
2. Open browser to http://localhost:5000
3. Upload CSV file with columns:
    * Symbol
    * Date/Time
    * Quantity
    * T. Price
    * Proceeds
    * Basis
    * Realized P/L
    * Local Development

## Local Development
```bash
export FLASK_ENV=development
export FLASK_APP=src/app.py
flask run
```