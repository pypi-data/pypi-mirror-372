"""CyberSource Adapter Module"""

from typing import Literal, Union

from sincpro_framework import logger

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource.domain import BillingInformation, Card, CardCVV
from sincpro_payments_sdk.apps.cybersource.domain.payments import (
    CaptureState,
    LinkSerMMDRequired,
    PaymentAuthorizationStatus,
)
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .common import (
    CyberSourceAuth,
    CyberSourceBaseResponse,
    LinkResponse,
    PayerAuthenticationResponse,
    create_merchant_def_map,
    cybersource_credential_provider,
)


class TransactionApiResponse(CyberSourceBaseResponse):
    status: PaymentAuthorizationStatus


class PaymentAuthorizationApiResponse(CyberSourceBaseResponse):
    """Payment authorization response."""

    status: PaymentAuthorizationStatus
    order_information: dict
    link_payment_auth: LinkResponse
    link_payment_capture: LinkResponse
    link_reverse_auth: LinkResponse


class ReverseAuthApiResponse(CyberSourceBaseResponse):
    """Reverse authorization response."""

    status: Literal["REVERSED",]


class PaymentCaptureApiResponse(CyberSourceBaseResponse):
    """Payment capture response."""

    status: CaptureState | PaymentAuthorizationStatus
    order_information: dict
    link_payment_capture: LinkResponse
    link_void: LinkResponse


class RefundPaymentApiResponse(CyberSourceBaseResponse):
    """Refund payment response."""

    status: str
    order_information: dict
    link_refund: LinkResponse
    link_void: LinkResponse


class RefundCaptureApiResponse(CyberSourceBaseResponse):
    """Refund capture response."""

    status: str
    order_information: dict
    link_capture_refund: LinkResponse
    link_void_capture: LinkResponse


class VoidApiResponse(CyberSourceBaseResponse):
    """Void payment response."""

    raw_response: dict


def build_base_payment_authorization_payload(
    transaction_ref: str,
    cvv: CardCVV,
    amount: float,
    currency: CurrencyType,
    billing_info: BillingInformation,
    merchant_defined_data: LinkSerMMDRequired,
) -> dict:
    format_merchant_defined_data = create_merchant_def_map(merchant_defined_data)
    """Create Reusable Payload for Payment Authorization."""
    payload = {
        "clientReferenceInformation": {"code": transaction_ref},
        "paymentInformation": {
            "card": {
                "securityCode": cvv,
            }
        },
        "orderInformation": {
            "amountDetails": {"totalAmount": str(amount), "currency": currency},
            "billTo": {
                "firstName": billing_info.first_name,
                "lastName": billing_info.last_name,
                "address1": billing_info.address,
                "locality": billing_info.city_name,
                "administrativeArea": billing_info.city_code,
                "postalCode": billing_info.postal_code,
                "country": billing_info.country_code,
                "email": billing_info.email,
                "phoneNumber": billing_info.phone,
            },
        },
        "merchantDefinedInformation": format_merchant_defined_data,
    }
    return payload


class PaymentAdapter(ClientAPI):
    """Adapter for CyberSource Payment API requests.

    Step:
    - Payment Authorization
      - Check Payment Status
      - Payment Capture | OR | Payment Auth Reverse
    - Payment Capture Success
      - Payment Void
    - Payment Refund
      - Payment Refund Capture
    """

    ROUTE_AUTH_PAYMENTS = "/pts/v2/payments"
    ROUTE_AUTH_PAYMENT = "/pts/v2/payments/{id}"
    ROUTE_REVERSE_AUTH = "/pts/v2/payments/{id}/reversals"
    ROUTE_PAYMENT_CAPTURE = "/pts/v2/payments/{id}/captures"
    ROUTE_REFUND_PAYMENT = "/pts/v2/payments/{id}/refunds"
    ROUTE_REFUND_CAPTURE = "/pts/v2/captures/{id}/refunds"
    ROUTE_VOID_PAYMENT = "/pts/v2/payments/{id}/voids"
    ROUTE_CAPTURE = "/pts/v2/captures/{id}"
    ROUTE_CHECK_STATUS_PAYMENT = "/pts/v2/refresh-payment-status/{id}"

    def __init__(self):
        """Initialize with a CyberSource client."""
        super().__init__(auth=CyberSourceAuth(cybersource_credential_provider))

    @property
    def base_url(self):
        """Get the base URL for the CyberSource API."""
        updated_credentials = cybersource_credential_provider.get_credentials()
        return f"https://{updated_credentials.endpoint}"

    def direct_payment_with_3ds_enrollment(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: CardCVV,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,  # For fingerprint process
        payer_auth_ref_id: str | None = None,  # For 3DS Setup
        return_url: str | None = None,  # For 3DS Setup
        store_card: bool = False,
        with_stored_token: bool = False,
    ) -> Union[PaymentCaptureApiResponse, PayerAuthenticationResponse]:
        """Direct payment with 3DS Enrollment.
        - Payer Auth Enrollment
        - Authorize payment
            - Fingerprint
        - Capture payment
        in One Step
        """
        payload = build_base_payment_authorization_payload(
            transaction_ref,
            cvv,
            amount,
            currency,
            billing_info,
            merchant_defined_data,
        )

        # 3DS Enrollment
        payload["processingInformation"] = {
            "fingerprintSessionId": fingerprint_token,
            "actionList": ["CONSUMER_AUTHENTICATION"],
            "capture": True,
        }

        # FingerPrint
        payload["deviceInformation"] = {"fingerprintSessionId": fingerprint_token}
        if payer_auth_ref_id:
            payload["consumerAuthenticationInformation"] = {
                "referenceId": payer_auth_ref_id,
                "returnUrl": return_url,
            }

        # Payment Detail
        if token_id and not card:
            payload["paymentInformation"]["paymentInstrument"] = {"id": token_id}

            if store_card:
                store_param = {"initiator": {"credentialStoredOnFile": store_card}}
                payload["processingInformation"]["authorizationOptions"] = store_param

            if with_stored_token:
                with_stored_token_params = {
                    "initiator": {"storedCredentialUsed": with_stored_token}
                }
                payload["processingInformation"][
                    "authorizationOptions"
                ] = with_stored_token_params

        if card and not token_id:
            card_payload = payload["paymentInformation"]["card"]
            card_payload["number"] = card.card_number
            card_payload["expirationMonth"] = card.month
            card_payload["expirationYear"] = card.year
            card_payload["type"] = card.card_type
        response = self.execute_request(
            self.ROUTE_AUTH_PAYMENTS,
            "POST",
            data=payload,
        )
        res_py_obj = response.json()

        status = PaymentAuthorizationStatus(res_py_obj.get("status"))
        match status:
            case PaymentAuthorizationStatus.PENDING_AUTHENTICATION:
                return PayerAuthenticationResponse(
                    raw_response=res_py_obj,
                    id=res_py_obj.get("id"),
                    status=status,
                    auth_transaction_id=res_py_obj["consumerAuthenticationInformation"][
                        "authenticationTransactionId"
                    ],
                    client_ref_info=res_py_obj["clientReferenceInformation"]["code"],
                    cavv=res_py_obj["consumerAuthenticationInformation"].get("cavv", None),
                    challenge_required=res_py_obj["consumerAuthenticationInformation"].get(
                        "challengeRequired", None
                    ),
                    access_token=res_py_obj["consumerAuthenticationInformation"].get(
                        "accessToken", None
                    ),
                    step_up_url=res_py_obj["consumerAuthenticationInformation"].get(
                        "stepUpUrl", None
                    ),
                    token=res_py_obj["consumerAuthenticationInformation"].get("token", None),
                )
            case _:
                return PaymentCaptureApiResponse(
                    id=res_py_obj["id"],
                    status=status,
                    order_information=res_py_obj.get("orderInformation", dict()),
                    link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
                    link_void=LinkResponse(**res_py_obj["_links"]["void"]),
                    raw_response=res_py_obj,
                )

    def direct_payment_with_3ds_validation(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: CardCVV,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,  # For fingerprint process
        auth_transaction_id: str | None = None,  # For 3DS Enrollment
        cavv: str | None = None,  # For 3DS Enrollment
        store_card: bool = False,  # Pay with token
        with_stored_token: bool = False,  # Pay with token
    ) -> Union[TransactionApiResponse]:
        """Direct payment with 3DS Enrollment.
        - Payer Auth Enrollment
        - Authorize payment
            - Fingerprint
        - Capture payment
        in One Step
        """
        payload = build_base_payment_authorization_payload(
            transaction_ref,
            cvv,
            amount,
            currency,
            billing_info,
            merchant_defined_data,
        )

        # 3DS Validation
        payload["processingInformation"] = {
            "fingerprintSessionId": fingerprint_token,
            "actionList": ["VALIDATE_CONSUMER_AUTHENTICATION"],
            "capture": True,
        }

        if auth_transaction_id or cavv:
            payload["consumerAuthenticationInformation"] = dict()
            logger.debug(
                f"Adding Consumer Authentication Information [{auth_transaction_id=}, {cavv=}]"
            )

        if auth_transaction_id:
            payload["consumerAuthenticationInformation"][
                "authenticationTransactionId"
            ] = auth_transaction_id

        if cavv:
            payload["consumerAuthenticationInformation"]["cavv"] = cavv

        # Payment Detail
        if token_id and not card:
            payload["paymentInformation"]["paymentInstrument"] = {"id": token_id}

            if store_card:
                store_param = {"initiator": {"credentialStoredOnFile": store_card}}
                payload["processingInformation"]["authorizationOptions"] = store_param

            if with_stored_token:
                with_stored_token_params = {
                    "initiator": {"storedCredentialUsed": with_stored_token}
                }
                payload["processingInformation"][
                    "authorizationOptions"
                ] = with_stored_token_params

        if card and not token_id:
            card_payload = payload["paymentInformation"]["card"]
            card_payload["number"] = card.card_number
            card_payload["expirationMonth"] = card.month
            card_payload["expirationYear"] = card.year
            card_payload["type"] = card.card_type

        response = self.execute_request(
            self.ROUTE_AUTH_PAYMENTS,
            "POST",
            data=payload,
        )
        res_py_obj = response.json()

        return TransactionApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            raw_response=res_py_obj,
        )

    def direct_payment(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: CardCVV,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,  # For fingerprint process
        auth_transaction_id: str | None = None,  # For 3DS Enrollment
        cavv: str | None = None,  # For 3DS Enrollment
    ) -> PaymentCaptureApiResponse:
        """Direct payment with CyberSource.
        - Authorize payment
            - Fingerprint
        - Capture payment
        in One Step
        """
        payload = build_base_payment_authorization_payload(
            transaction_ref,
            cvv,
            amount,
            currency,
            billing_info,
            merchant_defined_data,
        )
        payload["processingInformation"] = {"capture": True}
        payload["deviceInformation"] = {"fingerprintSessionId": fingerprint_token}

        if token_id and not card:
            payload["paymentInformation"]["paymentInstrument"] = {"id": token_id}

        if card and not token_id:
            card_payload = payload["paymentInformation"]["card"]
            card_payload["number"] = card.card_number
            card_payload["expirationMonth"] = card.month
            card_payload["expirationYear"] = card.year
            card_payload["type"] = card.card_type

        if auth_transaction_id or cavv:
            payload["consumerAuthenticationInformation"] = dict()

        if auth_transaction_id:
            payload["consumerAuthenticationInformation"]["authenticationTransactionId"] = (
                auth_transaction_id,
            )
        if cavv:
            payload["consumerAuthenticationInformation"]["cavv"] = cavv

        response = self.execute_request(
            self.ROUTE_AUTH_PAYMENTS,
            "POST",
            data=payload,
        )
        res_py_obj = response.json()

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def payment_authorization(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: CardCVV,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        transaction_session_id: str,
        auth_transaction_id: str | None = None,
        cavv: str | None = None,
    ) -> PaymentAuthorizationApiResponse:
        """
        Create a payment Authentication with CyberSource.
        """
        payload = build_base_payment_authorization_payload(
            transaction_ref,
            cvv,
            amount,
            currency,
            billing_info,
            merchant_defined_data,
        )

        payload["deviceInformation"] = {"fingerprintSessionId": transaction_session_id}

        if token_id and not card:
            payload["paymentInformation"]["paymentInstrument"] = {"id": token_id}

        if card and not token_id:
            card_payload = payload["paymentInformation"]["card"]
            card_payload["number"] = card.card_number
            card_payload["expirationMonth"] = card.month
            card_payload["expirationYear"] = card.year
            card_payload["type"] = card.card_type

        if auth_transaction_id or cavv:
            payload["consumerAuthenticationInformation"] = dict()

        if auth_transaction_id:
            payload["consumerAuthenticationInformation"]["authenticationTransactionId"] = (
                auth_transaction_id,
            )
        if cavv:
            payload["consumerAuthenticationInformation"]["cavv"] = cavv

        response = self.execute_request(
            self.ROUTE_AUTH_PAYMENTS,
            "POST",
            data=payload,
        )
        res_py_obj = response.json()
        return PaymentAuthorizationApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_payment_auth=LinkResponse(**res_py_obj["_links"]["self"]),
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["capture"]),
            link_reverse_auth=LinkResponse(**res_py_obj["_links"]["authReversal"]),
            raw_response=res_py_obj,
        )

    def get_auth_payment(self, payment_id: str) -> CyberSourceBaseResponse:
        """Check the status of a payment."""
        response = self.execute_request(
            self.ROUTE_AUTH_PAYMENT.format(id=payment_id),
            "GET",
        )
        res_py_obj = response.json()
        return CyberSourceBaseResponse(id=res_py_obj["id"], raw_response=res_py_obj)

    def reverse_auth_payment(
        self,
        payment_id: str,
        reason: str,
        transaction_ref: str,
        amount: float,
        currency: CurrencyType,
    ) -> ReverseAuthApiResponse:
        """Reverse a payment authorization with CyberSource."""
        payload = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
            "reason": reason,
        }
        response = self.execute_request(
            self.ROUTE_REVERSE_AUTH.format(id=payment_id),
            "POST",
            data=payload,
        )
        res_py_obj = response.json()

        return ReverseAuthApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            raw_response=res_py_obj,
        )

    def capture_payment(
        self, payment_id: str, transaction_ref: str, amount: float, currency: CurrencyType
    ) -> PaymentCaptureApiResponse:
        """Capture a payment with CyberSource."""

        payload = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
        }
        response = self.execute_request(
            self.ROUTE_PAYMENT_CAPTURE.format(id=payment_id),
            method="POST",
            data=payload,
        )
        res_py_obj = response.json()
        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def get_capture_payment(self, capture_id: str) -> CyberSourceBaseResponse:
        """Get Metadata of capture payment."""
        res = self.execute_request(
            self.ROUTE_CAPTURE.format(id=capture_id),
            method="GET",
        )
        res_py_obj = res.json()
        return CyberSourceBaseResponse(id=res_py_obj["id"], raw_response=res_py_obj)

    def refund_payment(
        self, capture_id: str, transaction_ref: str, amount: float, currency: CurrencyType
    ) -> RefundPaymentApiResponse:
        """Refund

        :param capture_id: Capture Payment ID
        :param transaction_ref: Reference of the transaction from external service
        :param amount:
        :param currency:
        :return:
        """
        payload = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
        }
        response = self.execute_request(
            self.ROUTE_REFUND_PAYMENT.format(id=capture_id),
            method="POST",
            data=payload,
        )
        res_py_obj = response.json()
        return RefundPaymentApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_refund=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def capture_refund(
        self,
        capture_payment_id: str,
        transaction_ref: str,
        amount: float,
        currency: CurrencyType,
    ) -> RefundCaptureApiResponse:
        """Capture a refund."""
        payload = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
        }
        response = self.execute_request(
            self.ROUTE_REFUND_CAPTURE.format(id=capture_payment_id),
            "POST",
            data=payload,
        )
        res_py_obj = response.json()
        return RefundCaptureApiResponse(
            raw_response=res_py_obj,
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_capture_refund=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void_capture=LinkResponse(**res_py_obj["_links"]["void"]),
        )

    def cancel_payment(
        self,
        payment_id: str,
        transaction_ref: str,
    ) -> VoidApiResponse:
        """Cancel payment or known as void"""
        payload = {
            "clientReferenceInformation": {"code": transaction_ref},
        }
        response = self.execute_request(
            self.ROUTE_VOID_PAYMENT.format(id=payment_id),
            method="POST",
            data=payload,
        )
        res_py_obj = response.json()

        return VoidApiResponse(
            id=res_py_obj["id"],
            raw_response=res_py_obj,
        )
