# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["Adapter"]


class Adapter(BaseModel):
    id: str

    description: str

    name: str

    organization: str
