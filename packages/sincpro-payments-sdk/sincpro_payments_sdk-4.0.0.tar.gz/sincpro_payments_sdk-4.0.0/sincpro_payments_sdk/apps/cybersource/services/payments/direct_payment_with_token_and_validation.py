"""Use case to create an token payment in CyberSource one transaction."""

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
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


class CommandDirectPaymentWithTokenAndValidation(DataTransferObject):
    """Data Transfer Object to create an anonymous payment in CyberSource."""

    #: Payment info
    token_id: str
    card_cvv: str
    transaction_ref: str
    amount: float
    currency: str
    city_code: str
    city_name: str
    country_code: str

    #: Customer infor
    customer_id: str
    customer_firstname: str
    customer_lastname: str
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_postal_code: str

    #: LINKSER info CUSTOMER
    is_logged_user: bool
    source_transaction: SourceOptions
    customer_number_document: str

    #: LINKSER info COMPANY
    industry_sector: IndustrySectorOptions
    company_number_document: str
    company_name: str
    product_description: str

    #: Fingerprint
    fingerprint_token: str

    #: Authentication 3D
    auth_transaction_id: str | None = None
    cavv: str | None = None

    #: first time to store token
    store_card: bool | None = None

    #: notify use token, stored card
    with_payment_token: bool | None = None


class ResponseDirectPaymentWithTokenAndValidation(DataTransferObject):
    transaction_id: str
    status: PaymentAuthorizationStatus | PayerAuthenticationStatus
    raw_response: dict


@cybersource.feature(CommandDirectPaymentWithTokenAndValidation)
class DirectPaymentWithTokenAndValidation(Feature):
    """
    Create an anonymous payment in CyberSource.
    """

    def execute(
        self, dto: CommandDirectPaymentWithTokenAndValidation
    ) -> ResponseDirectPaymentWithTokenAndValidation:
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
        direct_payment = self.payment_adapter.direct_payment_with_3ds_validation(
            dto.transaction_ref,
            None,
            dto.token_id,
            card_cvv,
            amount.total_amount,
            amount.currency,
            billing_info,
            merchant_defined_data,
            dto.fingerprint_token,
            dto.auth_transaction_id,
            dto.cavv,
            store_card=bool(dto.store_card),
            with_stored_token=bool(dto.with_payment_token),
        )

        if direct_payment.status in [
            PaymentAuthorizationStatus.DECLINED,
            PaymentAuthorizationStatus.INVALID_REQUEST,
            PayerAuthenticationStatus.AUTHENTICATION_FAILED,
        ]:
            raise exceptions.SincproValidationError(
                f"Payment authorization failed: {direct_payment.status}"
            )

        return ResponseDirectPaymentWithTokenAndValidation(
            transaction_id=direct_payment.id,
            status=direct_payment.status,
            raw_response=direct_payment.raw_response,
        )
