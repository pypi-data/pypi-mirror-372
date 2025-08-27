# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ..._models import BaseModel

__all__ = ["DrmInstanceGetMemoryContextResponse"]


class DrmInstanceGetMemoryContextResponse(BaseModel):
    generated_at: datetime

    memory_context: str
