"""Provide origin model."""

import sys
from enum import Enum


class Origin(Enum):
    """Enum that holds different origins - i.e., sources where the scanning is initiated from."""

    CLI = 1
    DOCKER = 2
    IDE = 3
    CI = 4

    def __str__(self) -> str:
        """
        Convert Origin to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, origin: str) -> "Origin":
        """
        Convert string level to Origin object.

        :param origin: Origin of using the library
        :return: Origin object
        """
        try:
            return cls[origin.upper()]
        except KeyError:
            print(
                f"Error: nonexistent origin: {origin}, valid values are: {[str(e) for e in Origin]}.",
                file=sys.stderr,
            )
            sys.exit(2)
