from abc import ABC
from abc import abstractmethod
from typing import List

from ..abstract.modules import SyncModule, AsyncModule
from ..api import endpoints, async_endpoints
from ..models.token import TokenInfo


class AbstractMeModule(ABC):
    def __init__(self, parent, client):
        self._parent = parent
        self._client = client

    @abstractmethod
    def _fetch_info(self) -> TokenInfo:
        """
        Get information about the current API token.

        Returns:
            TokenInfo: Information about the API token.

        Raises:
            Exception: If there is an error fetching the token information.
        """
        ...

    def info(self) -> TokenInfo:
        """
        Get information about the current API token.

        Returns:
            TokenInfo: Information about the API token.

        Raises:
            Exception: If there is an error fetching the token information.
        """
        return self._fetch_info()

    def groups(self) -> List[str]:
        """
        Get a list of groups the current user belongs to.

        Returns:
            list[str]: A list of group IDs.

        Raises:
            Exception: If there is an error fetching the groups.
        """
        resp = self.info()
        return getattr(resp, "groups", []) or []


class SyncMeModule(SyncModule, AbstractMeModule):
    def __init__(self, parent, client):
        SyncModule.__init__(self, parent, client)
        AbstractMeModule.__init__(self, parent, client)

    def _fetch_info(self) -> TokenInfo:
        return endpoints.me(self._client)


class AsyncMeModule(AsyncModule, AbstractMeModule):
    def __init__(self, parent, client):
        AsyncModule.__init__(self, parent, client)
        AbstractMeModule.__init__(self, parent, client)

    async def _fetch_info(self) -> TokenInfo:
        resp = await async_endpoints.me(self._client)
        return TokenInfo.model_validate(resp)

    async def info(self) -> TokenInfo:
        return await self._fetch_info()

    async def groups(self) -> List[str]:
        resp = await self.info()
        return getattr(resp, "groups", []) or []
