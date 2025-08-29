"""Linkser credentials model."""

from sincpro_payments_sdk.infrastructure.pydantic import BaseModel


class LinkserCredentials(BaseModel):
    """Linkser API credentials for JWT authentication."""

    codigo_comercio: str  # 7-digit merchant code
    jwt_token: str  # JWT token for LINKSER-KEY header
    endpoint: str
    production_mode: bool = False
