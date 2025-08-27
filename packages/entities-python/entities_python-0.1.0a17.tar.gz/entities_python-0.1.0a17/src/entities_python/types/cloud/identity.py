# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["Identity"]


class Identity(BaseModel):
    id: str

    created_at: datetime

    memory: int

    model: str

    name: str

    organization: str

    locked_at: Optional[datetime] = None

    sleep_until: Optional[datetime] = None

    system_prompt: Optional[str] = None

    timezone: Optional[str] = None

    tools: Optional[List[str]] = None
