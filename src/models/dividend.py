from utils.utils import parse_numeric


class Dividend:
    def __init__(self, row):
        self.currency = row.iloc[2]
        self.date_time = row.iloc[3]
        self.symbol = row.iloc[4]
        self.amount = float(row.iloc[5])

# Dividends,Header,Currency,Date,Description,Amount,,,,,,,,,,,
# Dividends,Data,USD,2024-12-03,TBIL(US74933W4520) Cash Dividend USD 0.184283 per Share (Ordinary Dividend),19.03,,,,,,,,,,,
