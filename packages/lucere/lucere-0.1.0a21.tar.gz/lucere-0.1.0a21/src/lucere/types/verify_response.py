# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["VerifyResponse"]


class VerifyResponse(BaseModel):
    error: Optional[str] = None

    expires_in: Optional[float] = None
