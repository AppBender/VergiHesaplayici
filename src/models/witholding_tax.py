from utils.utils import parse_numeric


class WithholdingTax:
    """
    A class representing withholding tax information.

    Initializes a WithholdingTax object from row data with corresponding headers.

    Args:
        row: A row containing withholding tax data
        header_row: A row containing the headers/column names

    Attributes:
        description (str): Description of the withholding tax
        amount (float): Amount of the withholding tax
    """
    def __init__(self, row, header_row):
        self.description = row[header_row[header_row == 'Description'].index[0]]
        self.amount = parse_numeric(row[header_row[header_row == 'Amount'].index[0]])
