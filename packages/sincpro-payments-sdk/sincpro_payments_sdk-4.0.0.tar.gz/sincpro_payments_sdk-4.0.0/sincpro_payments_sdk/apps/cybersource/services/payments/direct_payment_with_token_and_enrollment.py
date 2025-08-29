"""Use case to create an token payment in CyberSource one transaction with enrollment"""

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.common import (
    PayerAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    AmountDetails,
    BillingInformation,
    CardCVV,
    CityCode,
    CityName,
    CountryCode,
    IndustrySectorOptions,
    LinkSerMMDRequired,
    PayerAuthenticationStatus,
    PaymentAuthorizationStatus,
    SourceOptions,
)


class CommandDirectPaymentWithTokenAndEnrollment(DataTransferObject):
    """Data Transfer Object to create an anonymous payment in CyberSource."""

    # Payment info
    token_id: str
    card_cvv: str
    transaction_ref: str
    amount: float
    currency: str
    city_code: str
    city_name: str
    country_code: str

    # Customer infor
    customer_id: str
    customer_firstname: str
    customer_lastname: str
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_postal_code: str

    # LINKSER info CUSTOMER
    is_logged_user: bool
    source_transaction: SourceOptions
    customer_number_document: str

    # LINKSER info COMPANY
    industry_sector: IndustrySectorOptions
    company_number_document: str
    company_name: str
    product_description: str

    #: Finger print id
    fingerprint_token: str

    #: Authentication 3D Payer setup
    payer_auth_ref_id: str
    return_url: str | None = None

    #: first time to register token
    store_card: bool | None = None

    #: notify to cybersource use previously stored token (stored card)
    with_payment_token: bool | None = None


class ResponseDirectPaymentWithTokenAndEnrollment(DataTransferObject):
    transaction_id: str
    status: PaymentAuthorizationStatus | PayerAuthenticationStatus
    raw_response: dict

    #: 3D Secure (Payer authentication response)
    auth_transaction_id: str | None = None
    cavv: str | None = None

    #: 3D secure challenge(Challenge data)
    challenge_required: str | None = None
    step_up_url: str | None = None
    access_token: str | None = None


@cybersource.feature(CommandDirectPaymentWithTokenAndEnrollment)
class DirectPaymentWithTokenAndEnrollment(Feature):
    """
    Create an anonymous payment in CyberSource.
    """

    def execute(
        self, dto: CommandDirectPaymentWithTokenAndEnrollment
    ) -> ResponseDirectPaymentWithTokenAndEnrollment:
        """Main execution"""
        card_cvv = CardCVV(dto.card_cvv)
        # 1 Billing
        billing_info = BillingInformation(
            first_name=dto.customer_firstname,
            last_name=dto.customer_lastname,
            email=dto.customer_email,
            phone=dto.customer_phone,
            address=dto.customer_address,
            city_code=CityCode(dto.city_code),
            city_name=CityName(dto.city_name),
            postal_code=dto.customer_postal_code,
            country_code=CountryCode(dto.country_code),
        )

        # 2 Amount
        amount = AmountDetails(
            total_amount=dto.amount,
            currency=CurrencyType(dto.currency),
        )

        # Required by LINKSER
        merchant_defined_data = LinkSerMMDRequired(
            merchant_defined_data_1="SI" if dto.is_logged_user else "NO",
            merchant_defined_data_7=f"{dto.customer_firstname} {dto.customer_lastname}",
            merchant_defined_data_9=dto.source_transaction,
            merchant_defined_data_11=dto.customer_number_document,
            merchant_defined_data_12=dto.customer_phone,
            merchant_defined_data_14=dto.industry_sector,
            merchant_defined_data_15=dto.company_number_document,
            merchant_defined_data_87=dto.company_number_document,
            merchant_defined_data_88=dto.company_name,
            merchant_defined_data_90=dto.product_description,
        )

        response_payment_with_token = self.payment_adapter.direct_payment_with_3ds_enrollment(
            dto.transaction_ref,
            None,
            dto.token_id,
            card_cvv,
            amount.total_amount,
            amount.currency,
            billing_info,
            merchant_defined_data,
            dto.fingerprint_token,
            dto.payer_auth_ref_id,
            return_url=dto.return_url,
            store_card=bool(dto.store_card),
            with_stored_token=bool(dto.with_payment_token),
        )

        if response_payment_with_token.status in [
            PaymentAuthorizationStatus.DECLINED,
            PaymentAuthorizationStatus.INVALID_REQUEST,
        ]:
            raise exceptions.SincproValidationError("The payment was declined")

        if (
            response_payment_with_token.status
            == PayerAuthenticationStatus.PENDING_AUTHENTICATION
        ):
            cybersource.logger.info(
                "Adicional authentication required",
                challenge_required=response_payment_with_token.challenge_required,
            )

        if isinstance(response_payment_with_token, PayerAuthenticationResponse):
            return ResponseDirectPaymentWithTokenAndEnrollment(
                transaction_id=response_payment_with_token.id,
                status=response_payment_with_token.status,
                raw_response=response_payment_with_token.raw_response,
                auth_transaction_id=response_payment_with_token.auth_transaction_id,
                cavv=response_payment_with_token.cavv,
                challenge_required=response_payment_with_token.challenge_required,
                step_up_url=response_payment_with_token.step_up_url,
                access_token=response_payment_with_token.access_token,
            )

        return ResponseDirectPaymentWithTokenAndEnrollment(
            transaction_id=response_payment_with_token.id,
            status=response_payment_with_token.status,
            raw_response=response_payment_with_token.raw_response,
        )
