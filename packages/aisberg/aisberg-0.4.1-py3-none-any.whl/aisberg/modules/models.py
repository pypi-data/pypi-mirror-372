from abc import ABC
from abc import abstractmethod
from typing import List

from ..abstract.modules import SyncModule, AsyncModule
from ..api import endpoints, async_endpoints
from ..models.models import Model


class AbstractModelsModule(ABC):
    def __init__(self, parent, client):
        self._parent = parent
        self._client = client

    @abstractmethod
    def list(self) -> List[Model]:
        """
        Get a list of available collections. Models are grouped by your belonging groups.

        Returns:
            List[GroupModels]: A list of available collections.

        Raises:
            ValueError: If no collections are found.
            Exception: If there is an error fetching the collections.
        """
        ...

    @abstractmethod
    def get(self, model_id: str) -> Model:
        """Get details of a specific model.

        Args:
            model_id (str): The ID of the model to retrieve.

        Returns:
            Model: The details of the specified model.

        Raises:
            ValueError: If the specified model is not found.
        """
        ...

    @abstractmethod
    def is_available(self, model_id: str) -> bool:
        """Check if a specific model is available.

        Args:
            model_id (str): The ID of the model to check.

        Returns:
            bool: True if the model is available, False otherwise.
        """
        ...

    @staticmethod
    def _get_model_by_id(models: List[Model], model_id: str) -> Model | None:
        for model in models:
            if model.id == model_id:
                return model
        return None


class SyncModelsModule(SyncModule, AbstractModelsModule):
    def __init__(self, parent, client):
        SyncModule.__init__(self, parent, client)
        AbstractModelsModule.__init__(self, parent, client)

    def list(self) -> List[Model]:
        return endpoints.models(self._client)

    def get(self, model_id: str) -> Model:
        models = self.list()
        model = self._get_model_by_id(models, model_id)
        if model is None:
            raise ValueError("No model found")
        return model

    def is_available(self, model_id: str) -> bool:
        try:
            self.get(model_id)
            return True
        except ValueError:
            return False


class AsyncModelsModule(AsyncModule, AbstractModelsModule):
    def __init__(self, parent, client):
        AsyncModule.__init__(self, parent, client)
        AbstractModelsModule.__init__(self, parent, client)

    async def list(self) -> List[Model]:
        return await async_endpoints.models(self._client)

    async def get(self, model_id: str) -> Model:
        models = await self.list()
        model = self._get_model_by_id(models, model_id)
        if model is None:
            raise ValueError("No model found")
        return model

    async def is_available(self, model_id: str) -> bool:
        try:
            await self.get(model_id)
            return True
        except ValueError:
            return False
