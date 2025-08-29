"""Infrastructure Interface"""

from typing import Callable, Generic, TypeVar

TypeCredentialProvider = TypeVar("TypeCredentialProvider")
CredentialGetter = Callable[[], TypeCredentialProvider]


class CredentialProvider(Generic[TypeCredentialProvider]):
    """Reusable class
    Use the class to get credentials from a provider
    >>> provider_x: CredentialProvider[AnyModelReturned] = CredentialProvider(get_credentials)
    """

    def __init__(self, get_credentials: CredentialGetter):
        """Initialize with required credentials."""
        self._get_credentials: CredentialGetter = get_credentials

    def set_loader_credentials(self, fn: CredentialGetter) -> None:
        """Set the credentials from a callable ref"""
        self._get_credentials = fn

    def get_credentials(self) -> TypeCredentialProvider:
        """Get the credentials from the callable ref"""
        return self._get_credentials()
