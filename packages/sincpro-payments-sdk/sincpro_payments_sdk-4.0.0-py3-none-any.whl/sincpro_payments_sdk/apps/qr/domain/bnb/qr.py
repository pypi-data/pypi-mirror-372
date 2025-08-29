"""QR BNB Model"""

from datetime import date, datetime
from enum import IntEnum, StrEnum
from typing import NewType

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.infrastructure.pydantic import BaseModel

QRId = NewType("QRId", int)


class QRStatus(IntEnum):
    """Status for a QR code."""

    NO_USED = 1
    USED = 2
    EXPIRED = 3
    WITH_ERROR = 4
    UN_KNOW = 99


class QRUsageType(StrEnum):
    """Usage type for a QR code."""

    SINGLE_USE = "SINGLE_USE"
    MULTIPLE_USE = "MULTIPLE_USE"
    UN_KNOW = "UN_KNOW"


class QRImage(BaseModel):
    """QR image."""

    qr_id: QRId
    qr_image: str | bytes | None


class QRInfo(BaseModel):
    """QR information."""

    qr_id: QRId
    currency: CurrencyType
    expiration_date: date | datetime
    amount: float
    description: str
    single_use: QRUsageType = QRUsageType.UN_KNOW
    status: QRStatus = QRStatus.UN_KNOW
    generated_datetime: datetime | None = None
    transaction_date: date | datetime | None = None
