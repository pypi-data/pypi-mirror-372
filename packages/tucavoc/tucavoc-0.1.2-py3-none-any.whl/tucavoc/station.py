"""Utilities for handling station."""

from dataclasses import dataclass, field


@dataclass
class Station:
    # 3 letter code
    abbreviation: str
    _abbreviation: str = field(init=False, repr=False)
    # Name of the station
    name: str = ""

    # setter and getter for the abbreviation
    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @abbreviation.setter
    def abbreviation(self, abbreviation: str):
        if not isinstance(abbreviation, str):
            raise TypeError("Abbreviation must be a string")
        if len(abbreviation) != 3:
            raise ValueError("Abbreviation must be 3 letters long")
        self._abbreviation = abbreviation.upper()
        if self._abbreviation != abbreviation:
            raise ValueError("Abbreviation must be upper case")
