"""Cancel QR"""

from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr


class CommandCancelQR(DataTransferObject):
    """Command to cancel QR."""

    qr_id: int


class ResponseCancelQR(DataTransferObject):
    """Response from cancelling QR."""

    cancelled: bool
    qr_id: int


@qr.feature(CommandCancelQR)
class CancelQR(Feature):
    """Cancel QR code."""

    def execute(self, dto: CommandCancelQR) -> ResponseCancelQR:
        """Cancel QR code."""
        self.bnb_qr_adapter.cancel_qr(dto.qr_id)
        return ResponseCancelQR(cancelled=True, qr_id=dto.qr_id)
