"""Provide display level model."""

import sys
from enum import Enum


class DisplayLevel(Enum):
    """Enum that holds different levels/statuses for check result."""

    SUCCESS = 0
    HINT = 1
    WARNING = 2
    ERROR = 3

    def __str__(self) -> str:
        """
        Convert DisplayLevel to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, level: str) -> "DisplayLevel":
        """
        Convert string level to DisplayLevel object.

        :param level: Check result level
        :return: DisplayLevel object
        """
        try:
            return cls[level.upper()]
        except KeyError:
            print(
                f"Error: nonexistent check status display level: {level}, "
                f"valid values are: {[str(e) for e in DisplayLevel]}.",
                file=sys.stderr,
            )
            sys.exit(2)
