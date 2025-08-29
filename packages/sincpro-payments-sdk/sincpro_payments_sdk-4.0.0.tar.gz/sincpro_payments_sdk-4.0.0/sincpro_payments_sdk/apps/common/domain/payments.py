"""Common domain module for general payments."""

from enum import StrEnum


class CurrencyType(StrEnum):
    """Currency type enumeration."""

    BOB = "BOB"
    USD = "USD"
