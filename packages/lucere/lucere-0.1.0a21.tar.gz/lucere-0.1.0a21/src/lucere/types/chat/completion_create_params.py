# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CompletionCreateParams", "Message", "Attachment"]


class CompletionCreateParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]

    model: Required[str]

    attachments: Optional[Iterable[Attachment]]

    max_tokens: Optional[int]

    stream: Optional[bool]

    temperature: Optional[float]

    user: Optional[str]


class Message(TypedDict, total=False):
    content: Required[str]

    role: Required[str]

    name: Optional[str]


class Attachment(TypedDict, total=False):
    download_url: Required[Annotated[str, PropertyInfo(alias="downloadUrl")]]

    filename: Required[str]

    type: Required[str]

    description: Optional[str]
