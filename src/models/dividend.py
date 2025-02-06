from utils.utils import parse_numeric


class Dividend:
    def __init__(self, row, header_row):
        self.currency = row[header_row[header_row == 'Currency'].index[0]]
        self.date = row[header_row[header_row == 'Date'].index[0]]
        self.description = row[header_row[header_row == 'Description'].index[0]]
        self.amount = float(row[header_row[header_row == 'Amount'].index[0]])
