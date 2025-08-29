"""Common DTOs for CyberSource REST API."""

import base64
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Callable

from requests.auth import AuthBase

from sincpro_payments_sdk.apps.cybersource.domain import (
    CybersourceCredential,
    CybersourceEndPoints,
    LinkSerMMDRequired,
    PayerAuthenticationStatus,
)
from sincpro_payments_sdk.infrastructure.client_api import ApiResponse
from sincpro_payments_sdk.infrastructure.provider_credentials import CredentialProvider
from sincpro_payments_sdk.infrastructure.pydantic import BaseModel


class CyberSourceBaseResponse(ApiResponse):
    id: str


class LinkResponse(BaseModel):
    """Link response."""

    href: str
    method: str


def create_merchant_def_map(merchant_defined_data: LinkSerMMDRequired) -> list[dict]:
    """Create a map of merchant defined data."""
    format_merchant_defined_data = list()
    for key, value in merchant_defined_data.model_dump().items():
        last_word = key.split("_")[-1]
        format_merchant_defined_data.append({"key": last_word, "value": value})
    return format_merchant_defined_data


class PayerAuthenticationResponse(CyberSourceBaseResponse):
    status: PayerAuthenticationStatus
    auth_transaction_id: str
    client_ref_info: str
    cavv: str | None = None
    challenge_required: str | None = None
    access_token: str | None = None
    step_up_url: str | None = None
    token: str | None = None


def generate_hash(body: str) -> str:
    """Generate a Base64-encoded SHA-256 digest for the request body."""
    _body_bytes = body
    if isinstance(body, str):
        _body_bytes = body.encode("utf-8")
    digest = hashlib.sha256(_body_bytes).digest()
    return base64.b64encode(digest).decode("utf-8")


def build_str_signature(secret_key: bytes, string_to_sign: str) -> str:
    """Build the signature for the HTTP request."""
    signature = base64.b64encode(
        hmac.new(
            secret_key,
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return signature


class CyberSourceAuth(AuthBase):
    """Custom authentication for CyberSource API requests."""

    def __init__(
        self,
        cybersource_credential_provider: CredentialProvider[CybersourceCredential],
    ):
        """
        Initialize with required CyberSource credentials.
        If you pass a callable, the credentials will call to the callable or fn ref
        and get the credentials from there.
        """
        self._cybersource_credentials_provider: CredentialProvider[CybersourceCredential] = (
            cybersource_credential_provider
        )
        self._set_credentials_from_callable_ref()

    def _set_credentials_from_callable_ref(self):
        _cybersource_credentials = self._cybersource_credentials_provider.get_credentials()
        self.key_id = _cybersource_credentials.key_id

        self.secret_key = _cybersource_credentials.secret_key
        if isinstance(_cybersource_credentials.secret_key, str):
            self.secret_key = base64.b64decode(_cybersource_credentials.secret_key)
        self.merchant_id = _cybersource_credentials.merchant_id
        self.profile_id = _cybersource_credentials.profile_id

    def generate_signature_for_get_method(
        self,
        method: str,
        resource: str,
        date: str,
        host: str,
    ):
        """Generate the HTTP GET Signature for CyberSource authentication."""
        string_to_sign = (
            f"host: {host}\n"
            f"v-c-date: {date}\n"
            f"(request-target): {method.lower()} {resource}\n"
            f"v-c-merchant-id: {self.merchant_id}"
        )

        signature_header = (
            f'keyid="{self.key_id}", '
            f'algorithm="HmacSHA256", '
            f'headers="host v-c-date (request-target) v-c-merchant-id", '
            f'signature="{build_str_signature(self.secret_key, string_to_sign)}"'
        )

        return signature_header

    def generate_signature_with_body(
        self, method: str, resource: str, date: str, digest: str, host: str
    ) -> str:
        """Generate the HTTP Signature for CyberSource authentication."""

        string_to_sign = (
            f"host: {host}\n"
            f"v-c-date: {date}\n"
            f"(request-target): {method.lower()} {resource}\n"
            f"digest: SHA-256={digest}\n"
            f"v-c-merchant-id: {self.merchant_id}"
        )

        signature_header = (
            f'keyid="{self.key_id}", '
            f'algorithm="HmacSHA256", '
            f'headers="host v-c-date (request-target) digest v-c-merchant-id", '
            f'signature="{build_str_signature(self.secret_key, string_to_sign)}"'
        )

        return signature_header

    def build_headers(self, method: str, resource: str, body: str, host: str) -> dict:
        """Build the required headers for CyberSource request authentication."""
        datetime_required_format = datetime.now(timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        headers = {
            "Content-Type": "application/json",
            "host": host,
            "v-c-merchant-id": self.merchant_id,
            "v-c-date": datetime_required_format,
        }

        if self.profile_id:
            headers["profile-id"] = self.profile_id

        match method.upper():
            case "GET":
                signature = self.generate_signature_for_get_method(
                    method, resource, datetime_required_format, host
                )
                headers["signature"] = signature
            case _:
                body_hash = generate_hash(body)
                signature = self.generate_signature_with_body(
                    method, resource, datetime_required_format, body_hash, host
                )
                headers["digest"] = f"SHA-256={body_hash}"
                headers["signature"] = signature

        return headers

    def __call__(self, request):
        """Customize the request with headers for CyberSource authentication."""
        self._set_credentials_from_callable_ref()

        body = request.body
        host = request.url.split("//")[-1].split("/")[0]
        resource = request.path_url

        headers = self.build_headers(request.method, resource, body, host)
        request.headers.update(headers)

        return request


TEST_MERCHANT_ID = "linkser_0821787"
TEST_KEY = "d06af926-b72f-413b-9909-13e91e8ab611"
TEST_SECRET_KEY = "5B0cIhSWIkE1+nDvVdeZrHtRPDbDCs73WPoZcv9Ye1I="
TEST_PROFILE_ID = None

_fn_getter_credential_example: Callable[[], CybersourceCredential | None] = (
    lambda: CybersourceCredential(
        key_id=TEST_KEY,
        secret_key=TEST_SECRET_KEY,
        merchant_id=TEST_MERCHANT_ID,
        profile_id=TEST_PROFILE_ID,
        endpoint=CybersourceEndPoints.SAND_BOX,
    )
)


cybersource_credential_provider = CredentialProvider[CybersourceCredential](
    _fn_getter_credential_example
)
