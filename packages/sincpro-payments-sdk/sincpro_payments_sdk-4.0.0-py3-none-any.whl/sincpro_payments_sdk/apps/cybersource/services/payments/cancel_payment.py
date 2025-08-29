"""Use case to cancel a payment in not devliered."""

from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource


class CmdCancelPayment(DataTransferObject):
    payment_id: str
    transaction_ref: str


class ResCancelPayment(DataTransferObject):
    id: str
    raw_response: dict


@cybersource.feature(CmdCancelPayment)
class CancelPayment(Feature):
    """Refund a payment in CyberSource."""

    def execute(self, dto: CmdCancelPayment) -> ResCancelPayment:
        """Main execution"""

        void_payment = self.payment_adapter.cancel_payment(
            dto.payment_id,
            dto.transaction_ref,
        )

        return ResCancelPayment(
            id=void_payment.id,
            raw_response=void_payment.raw_response,
        )
