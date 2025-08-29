"""List QR based on date use case."""

from datetime import date

from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain import QRInfo


class CommandListQRs(DataTransferObject):
    """Command to list QR codes."""

    qr_date: date


class ResponseListQRs(DataTransferObject):
    """Response from listing QR codes."""

    listed_qrs: list[QRInfo]
    total: int


@qr.feature(CommandListQRs)
class ListQRs(Feature):
    """List QR codes."""

    def execute(self, dto: CommandListQRs) -> ResponseListQRs:
        """List QR codes."""
        response_api = self.bnb_qr_adapter.list_generated_qr(dto.qr_date)

        return ResponseListQRs(
            listed_qrs=response_api,
            total=len(response_api),
        )
