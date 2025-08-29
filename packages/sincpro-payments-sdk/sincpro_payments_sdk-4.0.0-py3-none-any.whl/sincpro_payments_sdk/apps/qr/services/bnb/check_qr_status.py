"""Check QR Status"""

from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain import QRStatus


class CommandCheckQRStatus(DataTransferObject):
    """Command to check QR status."""

    qr_id: int


class ResponseCheckQRStatus(DataTransferObject):
    status: QRStatus


@qr.feature(CommandCheckQRStatus)
class CheckQRStatus(Feature):
    """Check QR status."""

    def execute(self, dto: CommandCheckQRStatus) -> ResponseCheckQRStatus:
        """Check QR status."""
        response_api = self.bnb_qr_adapter.get_qr_status(dto.qr_id)
        return ResponseCheckQRStatus(status=response_api)
