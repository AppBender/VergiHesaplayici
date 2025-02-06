import pandas as pd

from models.dividend import Dividend
from models.fee import Fee
from models.trade import Trade
from models.witholding_tax import WithholdingTax
from databases.file_db import FileDB


class CSVParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path, encoding='utf-8')
        self.db = FileDB()

    def parse(self):
        processed_data = []
        tax_rate = 0.15
        total_taxable_profit = 0
        total_tax_amount = 0
        total_net_profit = 0

        for idx, row in self.df.iterrows():
            try:
                if pd.isna(row.iloc[0]):
                    self.db.log_error(f"Skipping empty or invalid row {idx}")
                    continue

                if row.iloc[0] == 'Trades' and row.iloc[1] == 'Data':
                    trade = Trade(row)
                    taxable_profit, tax_amount, net_profit = trade.calculate_tax(tax_rate)

                    total_taxable_profit += taxable_profit
                    total_tax_amount += tax_amount
                    total_net_profit += net_profit

                    processed_row = {
                        'Type': 'Trade',
                        'Asset Category': trade.asset_category,
                        'Symbol': trade.symbol,
                        'Date/Time': trade.date_time,
                        'Quantity': f"{trade.quantity:.2f}",
                        'TradePrice': f"{trade.trade_price:.2f}",
                        'Proceeds': f"{trade.proceeds:.2f}",
                        'Commission': f"{trade.commission_fee:.2f}",
                        'RealizedProfit': f"{trade.realized_pl:.2f}",
                        'TaxableProfit': f"{taxable_profit:.2f}",
                        'TaxAmount': f"{tax_amount:.2f}",
                        'NetProfit': f"{net_profit:.2f}"
                    }
                    processed_data.append(processed_row)

                elif row.iloc[0] == 'Fees' and row.iloc[1] == 'Data':
                    fee = Fee(row)
                    processed_row = {
                        'Type': 'Fee',
                        'Symbol': fee.symbol,
                        'Date/Time': fee.date_time,
                        'Amount': f"{fee.amount:.2f}"
                    }
                    processed_data.append(processed_row)

                elif row.iloc[0] == 'Dividends' and row.iloc[1] == 'Data':
                    dividend = Dividend(row)
                    processed_row = {
                        'Type': 'Dividend',
                        'Symbol': dividend.symbol,
                        'Date/Time': dividend.date_time,
                        'Amount': f"{dividend.amount:.2f}"
                    }
                    processed_data.append(processed_row)

                elif row.iloc[0] == 'Withholding Tax' and row.iloc[1] == 'Data':
                    withholding_tax = WithholdingTax(row)
                    processed_row = {
                        'Type': 'Withholding Tax',
                        'Symbol': withholding_tax.symbol,
                        'Date/Time': withholding_tax.date_time,
                        'Amount': f"{withholding_tax.amount:.2f}"
                    }
                    processed_data.append(processed_row)
            except Exception as e:
                self.db.log_error(f"Error processing row {idx}: {str(e)}")

        # Dynamically generate fieldnames from processed data
        fieldnames = set()
        for row in processed_data:
            fieldnames.update(row.keys())
        fieldnames = list(fieldnames)

        summary = {
            'TotalTaxableProfit': f"{total_taxable_profit:.2f}",
            'TotalTaxAmount': f"{total_tax_amount:.2f}",
            'TotalNetProfit': f"{total_net_profit:.2f}"
        }

        return processed_data, summary, fieldnames
