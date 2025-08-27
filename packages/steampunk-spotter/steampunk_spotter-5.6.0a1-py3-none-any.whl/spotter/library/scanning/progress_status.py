"""Provide scan progress status model."""

import sys
from enum import Enum


class ProgressStatus(Enum):
    """Enum that holds different statuses for scan progress."""

    PENDING = 0
    STARTED = 1
    SUCCESS = 2
    FAILURE = 3
    RETRY = 4
    REVOKED = 5

    def __str__(self) -> str:
        """
        Convert ProgressStatus to lowercase string.

        :return: String in lowercase
        """
        return str(self.name.lower())

    @classmethod
    def from_string(cls, status: str) -> "ProgressStatus":
        """
        Convert string progress status to ProgressStatus object.

        :param status: Progress status
        :return: ProgressStatus object
        """
        try:
            return cls[status.upper()]
        except KeyError:
            print(
                f"Error: nonexistent progress status: {status}, "
                f"valid values are: {[str(e) for e in ProgressStatus]}.",
                file=sys.stderr,
            )
            sys.exit(2)
