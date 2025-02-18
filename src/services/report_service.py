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
            'Stopaj': {'USD': Decimal('0'), 'TL': Decimal('0')}
        }

    def process_report(self, file_path: str) -> bool:
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

            # Clean up temporary file
            try:
                os.remove(file_path)
            except Exception as e:
                self.logger.log_error(f"Temp file cleanup failed: {str(e)}")

            return True

        except Exception as e:
            self.logger.log_error(f"Rapor işlenirken hata: {str(e)}")
            return False

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
                self.totals[category]['TL'] += item.amount_tl

    def _get_category(self, section_name: str, item: Any) -> str:
        if section_name == "Trades":
            return "Opsiyon" if item.is_option else "Hisse Senedi"
        elif section_name == "Dividends":
            return "Temettü"
        elif section_name in ["Withholding Tax", "Fees"]:
            return "Stopaj"
        return ""
