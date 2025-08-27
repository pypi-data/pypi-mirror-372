# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RuntimeCreateParams"]


class RuntimeCreateParams(TypedDict, total=False):
    identity: Required[str]

    force_run: bool

    max_turns: int
