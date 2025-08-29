# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ThreadForwardParams"]


class ThreadForwardParams(TypedDict, total=False):
    to: Required[Union[str, List[str]]]

    bcc: Union[str, List[str]]

    cc: Union[str, List[str]]

    from_: Annotated[str, PropertyInfo(alias="from")]

    from_name: str

    include_attachments: Annotated[bool, PropertyInfo(alias="includeAttachments")]

    is_draft: bool

    note: str
