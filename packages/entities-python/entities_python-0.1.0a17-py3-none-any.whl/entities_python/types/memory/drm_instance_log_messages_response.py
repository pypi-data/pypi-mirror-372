# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["DrmInstanceLogMessagesResponse"]


class DrmInstanceLogMessagesResponse(BaseModel):
    success: bool

    error: Optional[str] = None

    message_count: Optional[int] = None
