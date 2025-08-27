from __future__ import annotations

"""Internal module handling the SDK *global default client*.

A single default client instance can be handy for small scripts where passing
around the client object feels like boiler-plate.  Advanced applications can
ignore this entirely and manage their own client instances explicitly.
"""

from typing import Optional, TYPE_CHECKING

__all__ = ["set_default_client", "get_default_client"]

if TYPE_CHECKING:  # pragma: no cover – import only for type checkers
    from .client import NekudaClient


def set_default_client(client: Optional["NekudaClient"]) -> None:  # noqa: D401
    """Register *client* as the global default.

    Pass ``None`` to clear the default.
    """

    from .client import NekudaClient  # local import to avoid circular deps

    global _default_client

    if client is not None and not isinstance(client, NekudaClient):
        raise TypeError("default client must be a NekudaClient instance or None")

    _default_client = client


def get_default_client() -> NekudaClient:  # noqa: D401
    """Return the global default client.

    Raises
    ------
    RuntimeError
        If no default client has been configured.
    """

    if _default_client is None:
        raise RuntimeError(
            "No default NekudaClient configured – call set_default_client() first.",
        )
    return _default_client


# Internal mutable state -------------------------------------------------------

# At runtime we don't need the concrete class, so keep annotation as string
_default_client: Optional["NekudaClient"] = None
