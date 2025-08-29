"""Create QR use case."""

from datetime import date, timedelta

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.bnb.qr import QRImage


class CommandCreateQR(DataTransferObject):
    """Command to create a QR code."""

    amount: float
    currency: str
    description: str
    extra_reference: str
    single_use: bool = True
    expiration_date: date | None = None


class ResponseCreateQR(QRImage):
    """Response from creating a QR code."""


@qr.feature(CommandCreateQR)
class CreateQR(Feature):
    """Create QR code."""

    def execute(self, dto: CommandCreateQR) -> ResponseCreateQR:
        """Create QR code."""
        currency = CurrencyType(dto.currency)
        qr_expiration_date = dto.expiration_date or date.today() + timedelta(weeks=1)
        response_api = self.bnb_qr_adapter.generate_qr(
            currency=currency,
            gloss=dto.description,
            amount=dto.amount,
            extra_metadata=dto.extra_reference,
            expiration_date=qr_expiration_date,
            single_use=dto.single_use,
            destination_account=1,
        )

        return ResponseCreateQR.model_validate(response_api)
