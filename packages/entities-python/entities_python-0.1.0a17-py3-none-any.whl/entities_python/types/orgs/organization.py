# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ..._models import BaseModel

__all__ = ["Organization"]


class Organization(BaseModel):
    id: str

    created_at: datetime

    name: str
