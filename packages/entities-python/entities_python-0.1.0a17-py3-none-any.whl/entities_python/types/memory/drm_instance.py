# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["DrmInstance"]


class DrmInstance(BaseModel):
    id: int

    created_at: datetime

    organization: str

    updated_at: datetime

    name: Optional[str] = None

    summarizer_model: Optional[str] = None
