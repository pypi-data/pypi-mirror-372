# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Check"]


class Check(BaseModel):
    masked: Optional[bool] = None
    """Indicates whether the result or data is masked/hidden."""

    message: Optional[str] = None
    """Additional message or explanation about the check result."""

    name: Optional[str] = None
    """Name or type of the check performed."""

    validate_: Optional[bool] = FieldInfo(alias="validate", default=None)
    """Result of the check, true if passed."""

    weight: Optional[int] = None
    """Importance or weight of the check, often used in scoring."""
