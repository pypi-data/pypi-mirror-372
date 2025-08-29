"""BNB Credential providers"""

from typing import Callable

from requests.auth import AuthBase
from sincpro_framework import logger

from sincpro_payments_sdk.apps.qr.domain import BNBEndPoints, QRBNBCredentials
from sincpro_payments_sdk.infrastructure.provider_credentials import CredentialProvider


class BNBQRAuth(AuthBase):

    def __init__(self, bnb_qr_credential_provider: CredentialProvider[QRBNBCredentials]):
        self._bnb_qr_credential_provider: CredentialProvider[QRBNBCredentials] = (
            bnb_qr_credential_provider
        )
        self.account_id: str | None = None
        self.authorization_id: str | None = None
        self.jwt_token: str | None = None

    def _set_credentials_from_callable_ref(self):
        credentials = self._bnb_qr_credential_provider.get_credentials()
        self.account_id = credentials.account_id
        self.authorization_id = credentials.authorization_id
        self.jwt_token = credentials.jwt_token

    def build_headers(self) -> dict:
        """Build headers for BNB authentication."""
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
        }
        return headers

    def __call__(self, request):
        """Customize the request with headers for CyberSource authentication."""
        self._set_credentials_from_callable_ref()

        headers = self.build_headers()
        request.headers.update(headers)
        logger.debug(f"Request headers: {request.headers}")

        return request


_fn_getter_credential_example: Callable[[], QRBNBCredentials | None] = (
    lambda: QRBNBCredentials(
        account_id="test", authorization_id="test", endpoint=BNBEndPoints.SAND_BOX
    )
)

bnb_qr_credential_provider = CredentialProvider[QRBNBCredentials](
    _fn_getter_credential_example
)
