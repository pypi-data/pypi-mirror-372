from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardYear4Digits,
)


class CommandCreatePaymentMethod(DataTransferObject):
    card_number: str
    month: str
    year: str


class ResponseCreatePaymentMethod(DataTransferObject):
    id: str
    status: str
    raw_response: dict | None = None


@cybersource.feature(CommandCreatePaymentMethod)
class CreatePaymentMethod(Feature):
    """
    Create a customer payment method in CyberSource.
    - Create a customer
    - Create a card
    - Associate card to customer
    """

    def execute(self, dto: CommandCreatePaymentMethod) -> ResponseCreatePaymentMethod:
        """Main execution"""
        card_exp_year = self._get_exp_year(dto)
        card_exp_month = CardMonthOrDay(dto.month)
        card_number = CardNumber(dto.card_number)
        card_type = self._define_card_type(card_number)

        tokenized_card = self.token_adapter.create_card(card_number)
        tokenized_card_id = tokenized_card.get("id")

        if tokenized_card.get("state", None) != "ACTIVE":
            raise exceptions.SincproValidationError("Card not active")

        payment_method_token = self.token_adapter.create_card_payment_method(
            tokenized_card_id,
            card_exp_month,
            card_exp_year,
            card_type,
        )
        return ResponseCreatePaymentMethod(
            id=payment_method_token.get("id"),
            status=payment_method_token.get("state"),
            raw_response=payment_method_token,
        )

    def _get_exp_year(self, dto) -> CardYear4Digits:
        """Get the expiration year in the correct format."""
        card_exp_year = dto.year
        if len(dto.year) == 2:
            card_exp_year = f"20{dto.year}"
        return CardYear4Digits(card_exp_year)

    def _define_card_type(self, card_number: str) -> str:
        """Define the card type based on the card number."""
        if card_number.startswith("4"):
            return "visa"
        if card_number.startswith("5"):
            return "mastercard"
        return "visa"
