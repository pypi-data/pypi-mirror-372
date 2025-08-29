"""Init transaction use case module."""

from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.payer_auth_adapter import (
    SetupAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardType,
    CardYear4Digits,
)


class CommandStartMonitorAuth(DataTransferObject):
    """Data Transfer Object to prepare a payment in CyberSource."""

    card_type: CardType | str
    card_number: str
    card_month: str
    card_year: str
    transaction_ref: str


class ResponseStartMonitorAuth(SetupAuthenticationResponse):
    """Data Transfer Object to prepare a payment in CyberSource."""


@cybersource.feature(CommandStartMonitorAuth)
class StartMonitorAuth(Feature):
    """Prepare a payment in CyberSource."""

    def execute(self, dto: CommandStartMonitorAuth) -> ResponseStartMonitorAuth:
        """Main execution"""
        response = self.payer_auth_adapter.setup_payer_auth(
            CardNumber(dto.card_number),
            CardMonthOrDay(dto.card_month),
            CardYear4Digits(dto.card_year),
            CardType(dto.card_type),
            dto.transaction_ref,
        )

        return ResponseStartMonitorAuth(
            **response.model_dump(),
        )
