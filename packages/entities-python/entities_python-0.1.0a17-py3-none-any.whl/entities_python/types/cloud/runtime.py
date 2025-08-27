# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel
from .status_enum import StatusEnum

__all__ = ["Runtime"]


class Runtime(BaseModel):
    id: str

    created_at: datetime

    current_turn: int

    identity: str

    status: StatusEnum
    """
    - `created` - Created
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """

    force_run: Optional[bool] = None

    max_turns: Optional[int] = None
