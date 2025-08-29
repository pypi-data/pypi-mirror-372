"""Wrapper pydantic module"""

from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Base model to use in the application."""

    model_config = {
        "arbitrary_types_allowed": True,
        "use_enum_values": True,
        "from_attributes": True,
    }
