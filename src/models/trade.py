from utils.utils import parse_numeric


class Trade:
    """
    A class representing a financial trade transaction.

    This class encapsulates trade-related information including symbol, quantity,
    trade price, proceeds, commission, and realized profit/loss. It also provides
    functionality to calculate tax implications.

    Parameters
    ----------
    row : pandas.Series
        A row from a DataFrame containing trade information.
    header_row : pandas.Series
        The header row containing column names for trade data.

    Attributes
    ----------
    symbol : str
        The trading symbol/ticker of the financial instrument.
    quantity : float
        The number of units traded.
    trade_price : float
        The price per unit at which the trade was executed.
    proceeds : float
        The total proceeds from the trade.
    commission : float
        The commission charged for the trade.
    realized_pl : float
        The realized profit or loss from the trade.

    Methods
    -------
    calculate_tax(tax_rate)
        Calculates the tax implications of the trade.

        Parameters:
            tax_rate (float): The applicable tax rate as a decimal.

        Returns:
            tuple: Contains (taxable_profit, tax_amount, net_profit)
                - taxable_profit (float): The amount subject to taxation
                - tax_amount (float): The calculated tax amount
                - net_profit (float): Profit after tax deduction
    """
    def __init__(self, row, header_row):
        self.symbol = row[header_row[header_row == 'Symbol'].index[0]]
        self.quantity = parse_numeric(row[header_row[header_row == 'Quantity'].index[0]])
        self.trade_price = parse_numeric(row[header_row[header_row == 'TradePrice'].index[0]])
        self.proceeds = parse_numeric(row[header_row[header_row == 'Proceeds'].index[0]])
        self.commission = parse_numeric(row[header_row[header_row == 'Commission'].index[0]])
        self.realized_pl = parse_numeric(row[header_row[header_row == 'Realized P/L'].index[0]])

    def calculate_tax(self, tax_rate):
        taxable_profit = max(self.realized_pl, 0)
        tax_amount = taxable_profit * tax_rate
        net_profit = self.realized_pl - tax_amount
        return taxable_profit, tax_amount, net_profit
