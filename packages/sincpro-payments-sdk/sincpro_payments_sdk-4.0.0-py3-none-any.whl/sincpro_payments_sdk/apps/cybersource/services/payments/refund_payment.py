"""Use case to refund a payment in CyberSource."""

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.domain import AmountDetails


class CommandRefundPayment(DataTransferObject):
    capture_payment_id: str
    transaction_ref: str
    amount: float
    currency: CurrencyType | str


class ResponseRefundPayment(DataTransferObject):
    refund_id: str
    capture_refund_id: str
    link_get_auth_refund: str
    link_auth_refund_void: str
    link_get_capture: str
    link_void_capture: str
    raw_response_refund: dict | None = None
    raw_response_capture_refund: dict | None = None


@cybersource.feature(CommandRefundPayment)
class RefundPayment(Feature):
    """Refund a payment in CyberSource."""

    def execute(self, dto: CommandRefundPayment) -> ResponseRefundPayment:
        """Main execution"""
        amount_detail = AmountDetails(total_amount=dto.amount, currency=dto.currency)

        refund_auth = self.payment_adapter.refund_payment(
            dto.capture_payment_id,
            dto.transaction_ref,
            amount_detail.total_amount,
            amount_detail.currency,
        )

        capture_refund = self.payment_adapter.capture_refund(
            dto.capture_payment_id,
            dto.transaction_ref,
            amount_detail.total_amount,
            amount_detail.currency,
        )

        return ResponseRefundPayment(
            refund_id=refund_auth.id,
            capture_refund_id=capture_refund.id,
            link_get_auth_refund=refund_auth.link_refund.href,
            link_auth_refund_void=refund_auth.link_void.href,
            link_get_capture=capture_refund.link_capture_refund.href,
            link_void_capture=capture_refund.link_void_capture.href,
            raw_response_refund=refund_auth.raw_response,
            raw_response_capture_refund=capture_refund.raw_response,
        )
