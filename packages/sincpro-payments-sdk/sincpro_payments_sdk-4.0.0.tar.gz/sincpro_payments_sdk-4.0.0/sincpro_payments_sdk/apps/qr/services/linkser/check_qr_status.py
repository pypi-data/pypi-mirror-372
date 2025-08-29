"""Check QR status use case for Linkser based on PRD."""

from pydantic import Field

from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.linkser.qr import QRStatusLinkser


class CommandCheckQRStatusLinkser(DataTransferObject):
    """Command to check QR status with Linkser according to PRD."""

    codigo_comercio: str = Field(..., pattern=r"^\d{7}$", description="7-digit merchant code")
    codigo_qr: str = Field(..., min_length=1, description="QR code identifier")


class ResponseCheckQRStatusLinkser(QRStatusLinkser):
    """Response from checking QR status with Linkser."""


@qr.feature(CommandCheckQRStatusLinkser)
class CheckQRStatusLinkser(Feature):
    """Check QR status with Linkser."""

    def execute(self, dto: CommandCheckQRStatusLinkser) -> ResponseCheckQRStatusLinkser:
        """Check QR status."""
        response_api = self.linkser_qr_adapter.check_qr_status(
            codigo_comercio=dto.codigo_comercio,
            codigo_qr=dto.codigo_qr,
        )

        return ResponseCheckQRStatusLinkser.model_validate(response_api)
