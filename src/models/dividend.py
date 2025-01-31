from utils.utils import parse_numeric


class Dividend:
    """
    A class representing a dividend transaction.

    This class processes dividend information from a data row using corresponding header information.

    Attributes:
        description (str): The description of the dividend transaction.
        amount (float): The monetary amount of the dividend, parsed as a numeric value.

    Args:
        row: A row of data containing dividend information.
        header_row: A row containing header information with column names.

    Note:
        The class expects 'Description' and 'Amount' columns to be present in the header_row.
        The Amount value is automatically parsed into a numeric format.
    """
    def __init__(self, row, header_row):
        self.description = row[header_row[header_row == 'Description'].index[0]]
        self.amount = parse_numeric(row[header_row[header_row == 'Amount'].index[0]])
