"""Res api adapter."""

from datetime import date
from enum import StrEnum

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.qr.domain import QRInfo, QRStatus
from sincpro_payments_sdk.apps.qr.domain.bnb.qr import QRImage
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .bnb_common import BNBQRAuth, bnb_qr_credential_provider


def raise_error_if_not_transaction_success(raw_dict_response: dict) -> None:
    """Raise an error if the transaction was not successful."""
    if raw_dict_response.get("success") is False:
        if raw_dict_response.get("message"):
            raise exceptions.SincproExternalServiceError(raw_dict_response.get("message"))
        raise exceptions.SincproExternalServiceError("The transaction was not successful")


class QRRoutes(StrEnum):
    """BNB QR API routes."""

    GENERATE_QR = "/main/getQRWithImageAsync"
    LIST_GENERATED_QR = "/main/getQRByGenerationDateAsync"
    GET_QR_STATUS = "/main/getQRStatusAsync"
    CANCEL_QR = "/main/CancelQRByIdAsync"


class QRBNBApiAdapter(ClientAPI):

    def __init__(self):
        super().__init__(auth=BNBQRAuth(bnb_qr_credential_provider))

    @property
    def base_url(self) -> str:
        """Get the base URL for the CyberSource API."""
        credentials = bnb_qr_credential_provider.get_credentials()
        return f"{credentials.endpoint}/QRSimple.API/api/v1"

    def generate_qr(
        self,
        currency: CurrencyType,
        gloss: str,
        amount: float,
        extra_metadata: str,
        expiration_date: date,
        single_use: bool = True,
        destination_account: int = 1,
    ) -> QRImage:
        """Generate a QR code."""
        payload = {
            "currency": currency,
            "gloss": gloss,
            "amount": amount,
            "extraMetadata": extra_metadata,
            "expirationDate": expiration_date.strftime("%Y-%m-%d"),
            "singleUse": single_use,
            "destinationAccount": destination_account,
        }
        response = self.execute_request(
            QRRoutes.GENERATE_QR,
            "POST",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        python_dict = response.json()
        raise_error_if_not_transaction_success(python_dict)
        return QRImage(
            qr_id=python_dict.get("id"),
            qr_image=python_dict.get("qr"),
        )

    def list_generated_qr(self, generation_date: date) -> list[QRInfo]:
        """List generated QR codes."""
        payload = {"generationDate": generation_date.strftime("%Y-%m-%d")}
        response = self.execute_request(
            QRRoutes.LIST_GENERATED_QR,
            "POST",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        response_dict = response.json()
        raise_error_if_not_transaction_success(response_dict)
        return [
            QRInfo(
                qr_id=qr.get("id"),
                currency=CurrencyType(qr.get("currency")),
                amount=qr.get("amount"),
                expiration_date=qr.get("expirationDate"),
                description=qr.get("gloss"),
            )
            for qr in response_dict.get("dTOqrDetails", [])
        ]

    def get_qr_status(self, qr_id: int) -> QRStatus:
        """Get the status of a QR code."""
        payload = {"qrId": qr_id}
        response = self.execute_request(
            QRRoutes.GET_QR_STATUS,
            "POST",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        res = response.json()
        raise_error_if_not_transaction_success(res)
        return QRStatus(res.get("statusId"))

    def cancel_qr(self, qr_id: int) -> None:
        """Cancel a QR code."""
        payload = {"qrId": qr_id}
        response = self.execute_request(
            QRRoutes.CANCEL_QR,
            "POST",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        res_dict = response.json()
        raise_error_if_not_transaction_success(res_dict)
