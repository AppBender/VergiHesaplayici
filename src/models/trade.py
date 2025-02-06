from utils.utils import parse_numeric


class Trade:
    def __init__(self, row):
        self.data_discriminator = row.iloc[2]
        self.asset_category = row.iloc[3]
        self.currency = row.iloc[4]
        self.symbol = row.iloc[5]
        self.date_time = str(row.iloc[6])  # Ensure date_time is a string
        self.quantity = float(row.iloc[7])
        self.trade_price = float(row.iloc[8])
        self.current_price = float(row.iloc[9])
        self.proceeds = float(row.iloc[10])
        self.commission_fee = float(row.iloc[11])
        self.basis = float(row.iloc[12])
        self.realized_pl = float(row.iloc[13])
        self.mtm_pl = float(row.iloc[14])
        self.code = row.iloc[15]

    def calculate_tax(self, tax_rate):
        taxable_profit = self.realized_pl
        tax_amount = taxable_profit * tax_rate
        net_profit = taxable_profit - tax_amount
        return taxable_profit, tax_amount, net_profit
