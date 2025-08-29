# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EmailSendParams"]


class EmailSendParams(TypedDict, total=False):
    from_: Required[Annotated[str, PropertyInfo(alias="from")]]

    html: Required[str]

    subject: Required[str]

    to: Required[Union[str, List[str]]]

    bcc: Union[str, List[str]]

    cc: Union[str, List[str]]

    from_name: str

    in_reply_to: str

    is_draft: bool

    references: List[str]

    reply_to: Union[str, List[str]]

    text: str

    thread_id: Annotated[str, PropertyInfo(alias="threadId")]
