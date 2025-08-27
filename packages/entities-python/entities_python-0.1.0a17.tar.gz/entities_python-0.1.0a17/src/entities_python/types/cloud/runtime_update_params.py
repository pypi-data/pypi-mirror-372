# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["RuntimeUpdateParams"]


class RuntimeUpdateParams(TypedDict, total=False):
    force_run: bool

    identity: str

    max_turns: int
