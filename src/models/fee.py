from utils.utils import parse_numeric


class Fee:
    def __init__(self, row, header_row):
        self.description = row[header_row[header_row == 'Description'].index[0]]
        self.amount = parse_numeric(row[header_row[header_row == 'Amount'].index[0]])
