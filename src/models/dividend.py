from utils.utils import parse_numeric


class Dividend:
    def __init__(self, row):
        self.currency = row.iloc[2]
        self.date = row.iloc[3]
        self.description = row.iloc[4]
        self.amount = float(row.iloc[5])
