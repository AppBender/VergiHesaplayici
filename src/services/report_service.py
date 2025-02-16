from typing import List, Dict, Any
from decimal import Decimal
import pandas as pd
import csv
from protocols.parser_protocol import ParserProtocol
from protocols.report_writer_protocol import ReportWriterProtocol
from utils.csv_preprocessor import CSVPreprocessor
from services.logger_service import LoggerService


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
            # CSV dosyasını preprocess et ve oku
            df = CSVPreprocessor.preprocess(file_path)

            # Başlığı yaz
            self.writer.write_header()

            # Her bölümü işle
            sections = self._split_into_sections(df)
            for section_name, section_df in sections:
                parser = self._find_parser(section_name)
                if parser:
                    parsed_data = parser.parse(section_df)
                    self._update_totals(section_name, parsed_data)
                    self.writer.write_section(section_name, parsed_data)

            # Özeti yaz
            self.writer.write_summary(self.totals)
            return True

        except Exception as e:
            error_msg = f"Rapor işlenirken hata oluştu: {str(e)}"
            self.logger.log_error(error_msg)
            return False

    def _split_into_sections(self, df: pd.DataFrame) -> List[tuple[str, pd.DataFrame]]:
        sections = []
        current_section = None
        current_rows = []

        for _, row in df.iterrows():
            if row[0] != current_section and row[1] == "Header":
                if current_section and current_rows:
                    sections.append((current_section, pd.DataFrame(current_rows)))
                current_section = row[0]
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
        category = self._get_category(section_name)
        if category:
            for item in data:
                self.totals[category]['USD'] += item.amount_usd
                self.totals[category]['TL'] += item.amount_tl

    def _get_category(self, section_name: str) -> str:
        categories = {
            'Trades': 'Hisse Senedi',
            'Options': 'Opsiyon',
            'Dividends': 'Temettü',
            'Withholding Tax': 'Stopaj',
            'Fees': 'Stopaj'
        }
        return categories.get(section_name)
