"""Adapter for BNB Auth API."""

from enum import StrEnum

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.qr.domain import BNBEndPoints, QRBNBCredentials, UpdateAuthId
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .bnb_common import bnb_qr_credential_provider


class BNBAuthRoutes(StrEnum):
    """Routes for BNB Auth API."""

    JSON_WEB_TOKEN = "/auth/token"
    UPDATE_CREDENTIALS = "/auth/UpdateCredentials"


class BNBAuthAdapter(ClientAPI):

    def __init__(self):
        super().__init__()

    @property
    def base_url(self):
        """Get the base URL for the CyberSource API."""
        credentials = bnb_qr_credential_provider.get_credentials()
        return f"{credentials.endpoint}/ClientAuthentication.API/api/v1"

    def get_jwt(self, body: QRBNBCredentials) -> QRBNBCredentials:
        """Get JWT from BNB."""
        bnb_qr_credential_provider.set_loader_credentials(lambda: body)
        response = self.execute_request(
            BNBAuthRoutes.JSON_WEB_TOKEN,
            "POST",
            data={"accountId": body.account_id, "authorizationId": body.authorization_id},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        dict_response = response.json()
        jwt = dict_response.get("message")

        return QRBNBCredentials(
            account_id=body.account_id,
            authorization_id=body.authorization_id,
            jwt_token=jwt,
            endpoint=body.endpoint,
        )

    # TODO: cover this scenario
    def update_auth_id(self, body: UpdateAuthId) -> QRBNBCredentials:
        """Update the authorization ID."""
        response = self.execute_request(
            BNBAuthRoutes.UPDATE_CREDENTIALS,
            "POST",
            data={
                "accountId": body.account_id,
                "actualAuthorizationId": body.current_auth_id,
                "newAuthorizationId": body.new_auth_id,
            },
            headers={
                "Content-Type": "application/json",
                "cache-control": "no-cache",
                "Authorization": f"Bearer {body.jwt_token}",
            },
            timeout=15,
        )
        dict_response = response.json()

        if dict_response.get("success") is not True:
            raise exceptions.SincproExternalServiceError(
                "Error updating the authorization ID."
            )

        return QRBNBCredentials(
            account_id=body.account_id,
            authorization_id=body.new_auth_id,
            endpoint=BNBEndPoints.SAND_BOX,
        )
