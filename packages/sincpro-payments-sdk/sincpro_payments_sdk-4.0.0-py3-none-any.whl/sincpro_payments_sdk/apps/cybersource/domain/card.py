"""Card domain module."""

from enum import StrEnum
from typing import NewType

from pydantic.fields import computed_field

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.infrastructure.ddd import new_value_object
from sincpro_payments_sdk.infrastructure.pydantic import BaseModel


def validate_card_size(value: str):
    if len(value) != 16:
        raise exceptions.SincproValidationError("Card number must have 16 digits.")


def validate_cvv_size(value: str):
    """Check if the CVV is valid."""
    if len(value) != 3:
        raise exceptions.SincproValidationError("CVV must have 3 digits.")


def validate_month_or_day_size(month_or_day: str) -> None:
    """Check if the month and year are valid."""
    if len(month_or_day) < 2:
        raise exceptions.SincproValidationError("Month and year must have at least 2 digits")


def validate_year_size(year: str) -> None:
    """Check if the year is valid."""
    if len(year) != 4:
        raise exceptions.SincproValidationError("Year must have 4 digits")


# Value objects
CardNumber = new_value_object(NewType("CardNumber", str), validate_card_size)

CardCVV = new_value_object(NewType("CardCVV", str), validate_cvv_size)

CardMonthOrDay = new_value_object(
    NewType("CardDateAttribute", str), validate_month_or_day_size
)

CardYear4Digits = new_value_object(
    NewType("CardYear4Digits", str), validate_month_or_day_size
)


class CardType(StrEnum):
    """Card type enumeration."""

    UNKNOWN = "000"
    VISA = "001"
    MASTERCARD = "002"


def convert_to_card_type(card_number: CardNumber | str) -> CardType:
    """Convert a string to a card type."""
    if card_number.startswith("4"):
        return CardType.VISA
    elif card_number.startswith("5"):
        return CardType.MASTERCARD
    return CardType.UNKNOWN


class Card(BaseModel):
    card_number: CardNumber
    month: CardMonthOrDay
    year: CardYear4Digits

    @computed_field
    @property
    def card_type(self) -> CardType:
        """Get the card type."""
        return convert_to_card_type(self.card_number)
