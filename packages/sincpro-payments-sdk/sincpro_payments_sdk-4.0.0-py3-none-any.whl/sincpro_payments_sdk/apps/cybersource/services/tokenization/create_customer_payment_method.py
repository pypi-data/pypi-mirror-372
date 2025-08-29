from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource


class CommandCreateCustomerPaymentMethod(DataTransferObject):
    external_id: str
    email: str
    card_number: str
    card_type: str
    month: str
    year: str


class ResponseCreateCustomerPaymentMethod(DataTransferObject):
    raw_response: dict | None = None


@cybersource.feature(CommandCreateCustomerPaymentMethod)
class CreateCustomerPaymentMethod(Feature):
    """
    Create a customer payment method in CyberSource.
    - Create a customer
    - Create a card
    - Associate card to customer
    """

    def execute(
        self, dto: CommandCreateCustomerPaymentMethod
    ) -> ResponseCreateCustomerPaymentMethod:
        """Main execution"""
