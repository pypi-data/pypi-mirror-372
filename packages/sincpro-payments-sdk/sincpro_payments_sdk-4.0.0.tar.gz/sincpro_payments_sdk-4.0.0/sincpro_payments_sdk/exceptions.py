"""Exceptions module."""


class SincproValidationError(Exception):
    """Validation error exception."""

    def __init__(self, message):
        self.message = message


class SincproExternalServiceError(Exception):
    """External service error exception."""

    def __init__(self, message):
        self.message = message
