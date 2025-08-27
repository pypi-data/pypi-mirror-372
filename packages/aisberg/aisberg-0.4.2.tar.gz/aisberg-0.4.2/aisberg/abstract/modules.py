from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from ..client import AisbergClient
    from ..async_client import AisbergAsyncClient
    from httpx import Client as HttpClient
    from httpx import AsyncClient as AsyncHttpClient


class BaseModule(ABC):
    """Abstract base class for modules in the Aisberg framework."""

    def __init__(
        self,
        parent: Union["AisbergClient", "AisbergAsyncClient"],
        http_client: Optional[Union["HttpClient", "AsyncHttpClient"]] = None,
    ):
        """
        Initialize the BaseModule.

        Args:
            parent (Any): Parent client or module.
            http_client (Any): HTTP client for making requests.
        """
        self._parent = parent
        self._client = http_client


class SyncModule(BaseModule):
    """Abstract base class for synchronous modules in the Aisberg framework."""

    def __init__(self, parent: "AisbergClient", http_client: "HttpClient"):
        """
        Initialize the SyncModule.

        Args:
            parent (Any): Parent client or module.
            http_client (Any): HTTP client for making requests.
        """
        super().__init__(parent, http_client)


class AsyncModule(BaseModule):
    """Abstract base class for asynchronous modules in the Aisberg framework."""

    def __init__(self, parent: "AisbergAsyncClient", http_client: "AsyncHttpClient"):
        """
        Initialize the AsyncModule.

        Args:
            parent (Any): Parent client or module.
            http_client (Any): HTTP client for making requests.
        """
        super().__init__(parent, http_client)
