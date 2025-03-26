import os
import pandas as pd

from decimal import Decimal
from protocols.parser_protocol import ParserProtocol
from protocols.report_writer_protocol import ReportWriterProtocol
from services.logger_service import LoggerService
from typing import List, Dict, Any
from utils.csv_preprocessor import CSVPreprocessor


class ReportService:
    def __init__(
        self,
        parsers: List[ParserProtocol],
        writer: ReportWriterProtocol
    ):
        self.parsers = parsers
        self.writer = writer
        self.logger = LoggerService.get_instance()
        self.totals: Dict[str, Dict[str, Decimal]] = {
            'Hisse Senedi': {'USD': Decimal('0'), 'TL': Decimal('0')},
            'Opsiyon': {'USD': Decimal('0'), 'TL': Decimal('0')},
            'Temettü': {'USD': Decimal('0'), 'TL': Decimal('0')},
            'Stopaj': {'USD': Decimal('0'), 'TL': Decimal('0')},
            'Ücretler': {'USD': Decimal('0'), 'TL': Decimal('0')}  # Add fees
        }

    def process_report(self, file_path: str) -> Dict[str, Any]:
        """Process report and return tax summary"""
        try:
            # Preprocess CSV file
            df = CSVPreprocessor.preprocess(file_path)

            # Write header
            self.writer.write_header()

            # Process each section
            sections = self._split_into_sections(df)
            for section_name, section_df in sections:
                parser = self._find_parser(section_name)
                if parser:
                    parsed_data = parser.parse(section_df)
                    self._update_totals(section_name, parsed_data)
                    self.writer.write_section(section_name, parsed_data)

            # Write summary
            self.writer.write_summary(self.totals)

            # Calculate summary values
            stock_profit = self.totals.get('Hisse Senedi', {}).get('TL', Decimal('0'))
            option_profit = self.totals.get('Opsiyon', {}).get('TL', Decimal('0'))
            dividend_profit = self.totals.get('Temettü', {}).get('TL', Decimal('0'))
            withholding_tax = self.totals.get('Stopaj', {}).get('TL', Decimal('0'))
            fees = self.totals.get('Ücretler', {}).get('TL', Decimal('0'))

            # Calculate total taxable profit excluding fees
            total_taxable_profit = max(stock_profit + option_profit + dividend_profit + withholding_tax + fees, Decimal('0'))
            tax_rate = Decimal('0.15')  # 15% tax rate for 2024, this should be dynamic
            total_tax_amount = total_taxable_profit * tax_rate
            total_net_profit = total_taxable_profit - total_tax_amount

            # Clean up temporary file
            try:
                os.remove(file_path)
            except Exception as e:
                self.logger.log_error(f"Temp file cleanup failed: {str(e)}")

            # Return detailed summary
            return {
                'categories': {
                    'Hisse Senedi': {'USD': self.totals.get('Hisse Senedi', {}).get('USD', Decimal('0')),
                                    'TL': stock_profit},
                    'Opsiyon': {'USD': self.totals.get('Opsiyon', {}).get('USD', Decimal('0')),
                               'TL': option_profit},
                    'Temettü': {'USD': self.totals.get('Temettü', {}).get('USD', Decimal('0')),
                               'TL': dividend_profit},
                    'Stopaj': {'USD': self.totals.get('Stopaj', {}).get('USD', Decimal('0')),
                              'TL': withholding_tax},
                    'Ücretler': {'USD': self.totals.get('Ücretler', {}).get('USD', Decimal('0')),  # Add fees
                                'TL': fees}
                },
                'totals': {
                    'USD': sum(cat.get('USD', Decimal('0')) for cat in self.totals.values()),
                    'TL': sum(cat.get('TL', Decimal('0')) for cat in self.totals.values()),
                },
                'tax_summary': {
                    'taxable_profit': total_taxable_profit,
                    'tax_amount': total_tax_amount,
                    'net_profit': total_net_profit
                }
            }

        except Exception as e:
            self.logger.log_error(f"Rapor işlenirken hata: {str(e)}")
            raise

    def _split_into_sections(self, df: pd.DataFrame) -> List[tuple[str, pd.DataFrame]]:
        sections = []
        current_section = None
        current_rows = []

        for _, row in df.iterrows():
            section_name = row.iloc[0]
            if row.iloc[1] == "Header":
                if current_section and current_rows:
                    sections.append((current_section, pd.DataFrame(current_rows)))
                current_section = section_name
                current_rows = []
            current_rows.append(row)

        if current_section and current_rows:
            sections.append((current_section, pd.DataFrame(current_rows)))

        return sections

    def _find_parser(self, section_name: str) -> ParserProtocol:
        return next(
            (p for p in self.parsers if p.can_parse(section_name)),
            None
        )

    def _update_totals(self, section_name: str, data: List[Any]) -> None:
        for item in data:
            category = self._get_category(section_name, item)
            if category in self.totals:
                self.totals[category]['USD'] += item.amount_usd
                self.totals[category]['TL'] += item.taxable_amount_tl

    def _get_category(self, section_name: str, item: Any) -> str:
        if section_name == "Trades":
            return "Opsiyon" if item.is_option else "Hisse Senedi"
        elif section_name == "Dividends":
            return "Temettü"
        elif section_name == "Withholding Tax":
            return "Stopaj"
        elif section_name == "Fees":
            return "Ücretler"
        return ""
