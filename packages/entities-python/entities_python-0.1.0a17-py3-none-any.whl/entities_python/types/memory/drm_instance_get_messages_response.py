# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = ["DrmInstanceGetMessagesResponse", "DrmInstanceGetMessagesResponseItem"]


class DrmInstanceGetMessagesResponseItem(BaseModel):
    id: int

    created_at: datetime

    message_data: object

    timestamp: datetime


DrmInstanceGetMessagesResponse: TypeAlias = List[DrmInstanceGetMessagesResponseItem]
