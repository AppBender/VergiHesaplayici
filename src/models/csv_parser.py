import pandas as pd

from models.dividend import Dividend
from models.fee import Fee
from models.trade import Trade
from models.witholding_tax import WithholdingTax
from databases.file_db import FileDB


class CSVParser:
    """CSVParser class for processing financial data from CSV files.

    This class handles the parsing and processing of CSV files containing financial
    transaction data, including trades, fees, dividends, and withholding taxes.
    It calculates tax implications and provides summarized financial data.

    Attributes:
        file_path (str): Path to the CSV file to be processed
        df (pandas.DataFrame): DataFrame containing the CSV data
        section_headers (dict): Dictionary mapping section names to their starting row
        indices db (FileDB): Database instance for logging errors

    Methods:
        identify_section_headers(): Identifies the starting positions of different data
        sections parse(): Processes the CSV data and returns processed transactions with
        tax calculations

    Returns from parse():
        tuple: Contains three elements:
            - list: Processed transaction data as dictionaries
            - dict: Summary of calculations (total taxable profit, tax amount, net profit)
            - list: Field names for the processed data

    Raises:
        Various exceptions may be raised during file reading or data processing,
        which are caught and logged through the FileDB instance.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path, encoding='utf-8')
        self.section_headers = self.identify_section_headers()

    def identify_section_headers(self):
        """
        Identifies the starting indices of different sections in the DataFrame.

        This method scans through the DataFrame looking for specific section markers
        ('Trades', 'Fees', 'Dividends', 'Withholding Tax') and records the index of
        the row following each marker, which contains the actual headers for that section.

        Returns:
            dict: A dictionary mapping section names to their header row indices.
                  Keys are 'Trades', 'Fees', 'Dividends', 'Withholding Tax'.
                  Values are the index positions (int) of the header rows.
        """
        section_headers = {}
        for idx, row in self.df.iterrows():
            if row.iloc[0] == 'Trades':
                section_headers['Trades'] = idx + 1  # Next row is the header
            elif row.iloc[0] == 'Fees':
                section_headers['Fees'] = idx + 1
            elif row.iloc[0] == 'Dividends':
                section_headers['Dividends'] = idx + 1
            elif row.iloc[0] == 'Withholding Tax':
                section_headers['Withholding Tax'] = idx + 1
        return section_headers

    def parse(self):
        """
        Parses the loaded CSV data and processes it into structured format with tax
        calculations.

        The method processes different types of financial data including:
        - Trades (with tax calculations)
        - Fees
        - Dividends
        - Withholding Tax

        Returns:
            tuple: Contains three elements:
                - list: Processed data rows as dictionaries
                - dict: Summary of tax calculations including:
                    - TotalTaxableProfit
                    - TotalTaxAmount
                    - TotalNetProfit
                - list: Field names from all processed rows

        Raises:
            Exception: If there is an error processing any row (error will be logged)

        Note:
            - Empty or invalid rows are skipped and logged
            - All monetary values are formatted to 2 decimal places
            - Default tax rate is 15%
        """
        db = FileDB()
        processed_data = []
        tax_rate = 0.15
        total_taxable_profit = 0
        total_tax_amount = 0
        total_net_profit = 0

        for idx, row in self.df.iterrows():
            try:
                if row.empty or pd.isna(row.iloc[0]):
                    db.log_error(f"Skipping empty or invalid row {idx}")
                    continue

                if row.iloc[0] == 'Trades':
                    header_row = self.df.iloc[self.section_headers['Trades']]
                    trade = Trade(row, header_row)
                    taxable_profit, tax_amount, net_profit = trade.calculate_tax(tax_rate)

                    total_taxable_profit += taxable_profit
                    total_tax_amount += tax_amount
                    total_net_profit += net_profit

                    processed_row = {
                        'Type': 'Trade',
                        'Symbol': trade.symbol,
                        'Quantity': f"{trade.quantity:.2f}",
                        'TradePrice': f"{trade.trade_price:.2f}",
                        'Proceeds': f"{trade.proceeds:.2f}",
                        'Commission': f"{trade.commission:.2f}",
                        'RealizedProfit': f"{trade.realized_pl:.2f}",
                        'TaxableProfit': f"{taxable_profit:.2f}",
                        'TaxAmount': f"{tax_amount:.2f}",
                        'NetProfit': f"{net_profit:.2f}"
                    }
                    processed_data.append(processed_row)

                elif row.iloc[0] == 'Fees':
                    header_row = self.df.iloc[self.section_headers['Fees']]
                    fee = Fee(row, header_row)
                    processed_row = {
                        'Type': 'Fee',
                        'Description': fee.description,
                        'Amount': f"{fee.amount:.2f}"
                    }
                    processed_data.append(processed_row)

                elif row.iloc[0] == 'Dividends':
                    header_row = self.df.iloc[self.section_headers['Dividends']]
                    dividend = Dividend(row, header_row)
                    processed_row = {
                        'Type': 'Dividend',
                        'Description': dividend.description,
                        'Amount': f"{dividend.amount:.2f}"
                    }
                    processed_data.append(processed_row)

                elif row.iloc[0] == 'Withholding Tax':
                    header_row = self.df.iloc[self.section_headers['Withholding Tax']]
                    withholding_tax = WithholdingTax(row, header_row)
                    processed_row = {
                        'Type': 'Withholding Tax',
                        'Description': withholding_tax.description,
                        'Amount': f"{withholding_tax.amount:.2f}"
                    }
                    processed_data.append(processed_row)
            except Exception as e:
                db.log_error(f"Error processing row {idx}: {str(e)}")

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
