"""Use case to create an anonymous payment in CyberSource."""

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.common import (
    PayerAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    AmountDetails,
    BillingInformation,
    Card,
    CardCVV,
    CardMonthOrDay,
    CardNumber,
    CardYear4Digits,
    CityCode,
    CityName,
    CountryCode,
    IndustrySectorOptions,
    LinkSerMMDRequired,
    PayerAuthenticationStatus,
    PaymentAuthorizationStatus,
    SourceOptions,
)


class CommandDirectPaymentWithEnrollment(DataTransferObject):
    """Data Transfer Object to create an anonymous payment in CyberSource."""

    # Payment info
    transaction_ref: str
    amount: float
    currency: str
    card_number: str
    card_month: str
    card_year: str
    card_cvv: str
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

    #: Session id (FingerPrint)
    fingerprint_token: str

    #: Payer enrollment
    payer_auth_ref_id: str
    return_url: str | None = None


class ResponseDirectPaymentWithEnrollment(DataTransferObject):
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


@cybersource.feature(CommandDirectPaymentWithEnrollment)
class DirectPaymentWithEnrollment(Feature):
    """
    Create an anonymous payment in CyberSource.
    """

    def execute(
        self, dto: CommandDirectPaymentWithEnrollment
    ) -> ResponseDirectPaymentWithEnrollment:
        """Main execution"""
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

        # 2 Card
        card_number = CardNumber(dto.card_number)
        card_cvv = CardCVV(dto.card_cvv)
        month = CardMonthOrDay(dto.card_month)
        year = CardYear4Digits(dto.card_year)
        card = Card(
            card_number=card_number,
            month=month,
            year=year,
        )

        # 3 Amount
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

        direct_payment_response = self.payment_adapter.direct_payment_with_3ds_enrollment(
            dto.transaction_ref,
            card,
            None,
            card_cvv,
            amount.total_amount,
            amount.currency,
            billing_info,
            merchant_defined_data,
            dto.fingerprint_token,
            dto.payer_auth_ref_id,
            return_url=dto.return_url,
        )

        if direct_payment_response.status in [
            PaymentAuthorizationStatus.DECLINED,
            PaymentAuthorizationStatus.INVALID_REQUEST,
        ]:
            raise exceptions.SincproValidationError(
                f"Payment authorization failed for: {dto.transaction_ref}"
            )

        if direct_payment_response.status == PayerAuthenticationStatus.PENDING_AUTHENTICATION:
            cybersource.logger.info(
                "Adicional authentication required",
                challenge_required=direct_payment_response.challenge_required,
            )

        if isinstance(direct_payment_response, PayerAuthenticationResponse):
            return ResponseDirectPaymentWithEnrollment(
                transaction_id=direct_payment_response.id,
                status=direct_payment_response.status,
                raw_response=direct_payment_response.raw_response,
                auth_transaction_id=direct_payment_response.auth_transaction_id,
                cavv=direct_payment_response.cavv,
                challenge_required=direct_payment_response.challenge_required,
                step_up_url=direct_payment_response.step_up_url,
                access_token=direct_payment_response.access_token,
            )

        return ResponseDirectPaymentWithEnrollment(
            transaction_id=direct_payment_response.id,
            status=direct_payment_response.status,
            raw_response=direct_payment_response.raw_response,
        )
