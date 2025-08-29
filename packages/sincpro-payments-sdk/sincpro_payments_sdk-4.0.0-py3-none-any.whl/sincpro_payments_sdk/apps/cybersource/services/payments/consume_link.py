"""Consume generated link."""

from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource


class CommandConsumeLink(DataTransferObject):
    """DTO for ConsumeLink use case."""

    resource: str


class ResponseConsumeLink(DataTransferObject):
    """DTO for ConsumeLink use case."""

    raw_response: dict | None = None


@cybersource.feature(CommandConsumeLink)
class ConsumeLink(Feature):
    """Consume a generated link."""

    def execute(self, dto: CommandConsumeLink) -> ResponseConsumeLink:
        """Main execution"""
        response = self.payment_adapter.execute_request(dto.resource, "GET")
        return ResponseConsumeLink(raw_response=response.json())
