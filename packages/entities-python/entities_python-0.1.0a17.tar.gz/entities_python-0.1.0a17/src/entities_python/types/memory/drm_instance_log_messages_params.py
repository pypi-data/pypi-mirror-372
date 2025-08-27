# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DrmInstanceLogMessagesParams"]


class DrmInstanceLogMessagesParams(TypedDict, total=False):
    messages: Required[Iterable[object]]
    """Array of OpenAI-format messages"""

    timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Optional timestamp for all messages (defaults to now)"""
