# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TokenGenerateParams"]


class TokenGenerateParams(TypedDict, total=False):
    role: Required[str]

    user_id: Required[str]
