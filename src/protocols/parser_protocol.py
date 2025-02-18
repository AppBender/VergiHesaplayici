from typing import Protocol, TypeVar, List
import pandas as pd

T = TypeVar('T')


class ParserProtocol(Protocol[T]):
    """Protocol defining the interface for all parsers"""
    def can_parse(self, section_name: str) -> bool:
        """Check if this parser can handle the given section"""
        ...

    def parse(self, df: pd.DataFrame) -> List[T]:
        """Parse the data and return a list of domain objects"""
        ...
