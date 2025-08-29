from sincpro_framework import UseFramework

from sincpro_payments_sdk.apps.qr.adapters import (
    bnb_auth_adapter,
    bnb_qr_adapter,
    linkser_qr_adapter,
)
from sincpro_payments_sdk.apps.qr.adapters.bnb_common import (
    QRBNBCredentials,
    bnb_qr_credential_provider,
)
from sincpro_payments_sdk.apps.qr.adapters.linkser_qr_adapter import (
    linkser_qr_credential_provider,
)
from sincpro_payments_sdk.apps.qr.domain.linkser.credentials import LinkserCredentials
from sincpro_payments_sdk.infrastructure.provider_credentials import CredentialProvider


def register_dependencies(framework: UseFramework) -> UseFramework:
    """Register dependencies for the framework."""

    framework.add_dependency("credential_provider", bnb_qr_credential_provider)
    framework.add_dependency("bnb_auth_adapter", bnb_auth_adapter.BNBAuthAdapter())
    framework.add_dependency("bnb_qr_adapter", bnb_qr_adapter.QRBNBApiAdapter())
    framework.add_dependency("linkser_credential_provider", linkser_qr_credential_provider)
    framework.add_dependency("linkser_qr_adapter", linkser_qr_adapter.LinkserQRApiAdapter())
    return framework


class DependencyContextType:
    """Typing helper."""

    credential_provider: CredentialProvider[QRBNBCredentials]
    bnb_auth_adapter: bnb_auth_adapter.BNBAuthAdapter
    bnb_qr_adapter: bnb_qr_adapter.QRBNBApiAdapter
    linkser_credential_provider: CredentialProvider[LinkserCredentials]
    linkser_qr_adapter: linkser_qr_adapter.LinkserQRApiAdapter
