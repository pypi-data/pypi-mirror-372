from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `entities_python.resources` module.

    This is used so that we can lazily import `entities_python.resources` only when
    needed *and* so that users can just import `entities_python` and reference `entities_python.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("entities_python.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
