"""Generate QR use case for Linkser based on PRD."""

from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.linkser.qr import QRImageLinkser


class CommandGenerateQRLinkser(DataTransferObject):
    """Command to generate QR code with Linkser according to PRD."""

    codigo_comercio: str
    importe: float | str
    glosa: str


class ResponseGenerateQRLinkser(QRImageLinkser):
    """Response from generating QR code with Linkser."""


@qr.feature(CommandGenerateQRLinkser)
class GenerateQRLinkser(Feature):
    """Generate QR code with Linkser."""

    def execute(self, dto: CommandGenerateQRLinkser) -> ResponseGenerateQRLinkser:
        """Generate QR code."""
        response_api = self.linkser_qr_adapter.generate_qr(
            codigo_comercio=dto.codigo_comercio,
            importe=dto.importe,
            glosa=dto.glosa,
        )

        return ResponseGenerateQRLinkser.model_validate(response_api)
