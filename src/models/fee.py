from utils.utils import parse_numeric


class Fee:
    def __init__(self, row, header_row):
        self.currency = row[header_row[header_row == 'Currency'].index[0]]
        self.settle_date = row[header_row[header_row == 'Settle Date'].index[0]]
        self.description = row[header_row[header_row == 'Description'].index[0]]
        self.amount = float(row[header_row[header_row == 'Amount'].index[0]])
