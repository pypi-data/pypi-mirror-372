from sincpro_framework import UseFramework

from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api import (
    payer_auth_adapter,
    payment_adapter,
    tokenization_adapter,
)


class DependencyContextType:
    token_adapter: tokenization_adapter.TokenizationAdapter
    payment_adapter: payment_adapter.PaymentAdapter
    payer_auth_adapter: payer_auth_adapter.PayerAuthenticationAdapter


def register_dependencies(framework: UseFramework) -> UseFramework:
    """Register dependencies for the framework."""
    framework.add_dependency("token_adapter", tokenization_adapter.TokenizationAdapter())
    framework.add_dependency("payment_adapter", payment_adapter.PaymentAdapter())
    framework.add_dependency(
        "payer_auth_adapter", payer_auth_adapter.PayerAuthenticationAdapter()
    )
    return framework
