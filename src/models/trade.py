from utils.utils import parse_numeric


class Trade:
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
