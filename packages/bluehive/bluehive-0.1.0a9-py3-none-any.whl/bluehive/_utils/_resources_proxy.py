from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `bluehive.resources` module.

    This is used so that we can lazily import `bluehive.resources` only when
    needed *and* so that users can just import `bluehive` and reference `bluehive.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("bluehive.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
