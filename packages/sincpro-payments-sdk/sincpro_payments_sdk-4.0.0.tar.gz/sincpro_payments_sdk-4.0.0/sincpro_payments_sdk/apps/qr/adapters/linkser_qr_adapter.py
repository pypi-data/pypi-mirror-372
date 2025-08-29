"""Linkser QR API adapter based on PRD specification."""

import os
from enum import StrEnum

import requests
from requests.auth import AuthBase

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.qr.domain.linkser import (
    LinkserCredentials,
    QRImageLinkser,
    QRStatusLinkser,
)
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI
from sincpro_payments_sdk.infrastructure.provider_credentials import CredentialProvider


def _fn_credentials_example_getters() -> LinkserCredentials:
    """Load Linkser credentials from environment variables."""
    return LinkserCredentials(
        codigo_comercio=os.getenv("LINKSER_CODIGO_COMERCIO", "1234567"),
        jwt_token=os.getenv("LINKSER_JWT_TOKEN", "test_jwt_token"),
        endpoint=os.getenv("LINKSER_ENDPOINT", "https://api.linkser.com"),
        production_mode=os.getenv("LINKSER_PRODUCTION_MODE", "false").lower() == "true",
    )


linkser_qr_credential_provider = CredentialProvider[LinkserCredentials](
    _fn_credentials_example_getters
)


class LinkserJWTAuth(AuthBase):
    """Linkser JWT API authentication according to PRD."""

    def __init__(self, credential_provider: CredentialProvider[LinkserCredentials]):
        self.credential_provider = credential_provider

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Apply JWT authentication to the request."""
        credentials = self.credential_provider.get_credentials()

        r.headers.update(
            {
                "LINKSER-API-KEY": credentials.jwt_token,
                "Content-Type": "application/json",
            }
        )
        return r


def raise_error_if_not_transaction_success(raw_dict_response: dict) -> None:
    """Raise an error if the transaction was not successful."""
    # The PRD doesn't specify error response format, so we'll handle common patterns
    if "error" in raw_dict_response:
        raise exceptions.SincproExternalServiceError(raw_dict_response.get("error"))
    if raw_dict_response.get("success") is False:
        message = raw_dict_response.get("message", "The transaction was not successful")
        raise exceptions.SincproExternalServiceError(message)


class LinkserRoutes(StrEnum):
    """Linkser API routes according to PRD."""

    GENERATE_QR = "/wsTransactionsQR/linkser/generateQR"
    # Note: PRD doesn't specify the consultQR endpoint, this is an assumption
    CONSULT_QR = "/wsTransactionsQR/linkser/consultQR"


class LinkserQRApiAdapter(ClientAPI):
    """Linkser QR API adapter according to PRD specification."""

    def __init__(self):
        super().__init__(auth=LinkserJWTAuth(linkser_qr_credential_provider))

    @property
    def base_url(self) -> str:
        """Get the base URL for the Linkser API."""
        credentials = linkser_qr_credential_provider.get_credentials()
        return credentials.endpoint

    def generate_qr(
        self,
        codigo_comercio: str,
        importe: float | str,
        glosa: str,
    ) -> QRImageLinkser:
        """Generate a QR code according to PRD specification."""
        payload = {
            "codigo_comercio": codigo_comercio,
            "importe": str(importe).replace(".", ","),
            "glosa": glosa,
        }

        response = self.execute_request(
            LinkserRoutes.GENERATE_QR,
            "POST",
            data=payload,
            timeout=30,
        )

        python_dict = response.json()
        raise_error_if_not_transaction_success(python_dict)

        return QRImageLinkser(
            codigo_qr=python_dict.get("codigo_qr", ""),
            imagen_qr=python_dict.get("imagen_qr", ""),
            fecha_generacion=python_dict.get("fecha_generacion"),
            estado=python_dict.get("estado", "Pendiente"),
        )

    def check_qr_status(
        self,
        codigo_comercio: str,
        codigo_qr: str,
    ) -> QRStatusLinkser:
        """Check QR status according to PRD specification."""
        payload = {
            "codigo_comercio": codigo_comercio,
            "codigo_qr": codigo_qr,
        }

        response = self.execute_request(
            LinkserRoutes.CONSULT_QR,
            "POST",
            data=payload,
            timeout=30,
        )

        python_dict = response.json()
        raise_error_if_not_transaction_success(python_dict)

        # Map response to our domain model
        return QRStatusLinkser(
            codigo_qr=python_dict.get("codigo_qr", codigo_qr),
            estado=python_dict.get("estado", "Pendiente"),
            fecha_transaccion=python_dict.get("fecha_transaccion"),
            importe_pagado=python_dict.get("importe_pagado"),
        )
