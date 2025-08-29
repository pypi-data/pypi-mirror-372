"""Step 3: Validate if challenge was completed."""

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain.payments import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.common import (
    PayerAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardType,
    CardYear4Digits,
)


class CommandValidateAuth(DataTransferObject):
    """Validate Auth if challenge was successfull"""

    card_type: CardType | str
    card_number: CardNumber | str
    card_month: CardMonthOrDay | str
    card_year: CardYear4Digits | str
    transaction_ref: str
    amount: str | float
    currency: str


class ResponseValidateAuth(PayerAuthenticationResponse):
    """Response Validation Auth if challenge was successfull"""


@cybersource.feature(CommandValidateAuth)
class ValidateAuth(Feature):
    """Validate Auth feature"""

    def execute(self, dto: CommandValidateAuth) -> ResponseValidateAuth:
        """Main Function"""
        card = CardNumber(dto.card_number)
        month = CardMonthOrDay(dto.card_month)
        year = CardYear4Digits(dto.card_year)
        card_type = CardType(dto.card_type)

        enrollment = self.payer_auth_adapter.validate_auth(
            card,
            month,
            year,
            card_type,
            dto.transaction_ref,
            dto.amount,
            CurrencyType(dto.currency),
        )

        if enrollment.status == "AUTHENTICATION_FAILED":
            raise exceptions.SincproValidationError(
                "El banco no permite realizar transacion por falta de autenticacion"
            )

        return ResponseValidateAuth(**enrollment.model_dump())
