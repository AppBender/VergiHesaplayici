from utils.utils import parse_numeric


class Fee:
    """
    A class representing a fee entry from a data row.

    This class processes a row of data and extracts fee information based on the provided
    header row.

    Parameters
    ----------
    row : pandas.Series
        A row of data containing fee information.
    header_row : pandas.Series
        The header row containing column names.

    Attributes
    ----------
    description : str
        The description of the fee from the 'Description' column.
    amount : float
        The numeric amount of the fee from the 'Amount' column.
    """
    def __init__(self, row, header_row):
        self.description = row[header_row[header_row == 'Description'].index[0]]
        self.amount = parse_numeric(row[header_row[header_row == 'Amount'].index[0]])
