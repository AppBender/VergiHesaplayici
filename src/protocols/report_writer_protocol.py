from typing import Protocol, List, Any
from decimal import Decimal


class ReportWriterProtocol(Protocol):
    """Protocol defining the interface for report writers"""
    def write_header(self) -> None:
        """Write the report header"""
        ...

    def write_section(self, section_name: str, rows: List[Any]) -> None:
        """Write a section of the report"""
        ...

    def write_summary(self, totals: dict[str, dict[str, Decimal]]) -> None:
        """Write the report summary"""
        ...
