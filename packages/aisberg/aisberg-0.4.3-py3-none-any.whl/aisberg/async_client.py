from typing import Dict, Callable

import httpx

from .config import settings
from .modules import (
    AsyncChatModule,
    AsyncCollectionsModule,
    AsyncEmbeddingsModule,
    AsyncMeModule,
    AsyncModelsModule,
    AsyncWorkflowsModule,
    ToolsModule,
    AsyncDocumentsModule,
)


class AisbergAsyncClient:
    def __init__(self, base_url=None, api_key=None, timeout=None):
        self.api_key = api_key or settings.aisberg_api_key
        self.base_url = base_url or settings.aisberg_base_url
        self.timeout = (
            timeout or settings.aisberg_timeout
        )  # default to 180 seconds (3 minutes)
        self.tool_registry: Dict[str, Callable] = {}
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        # Modules
        self.tools = ToolsModule(self)
        self.chat = AsyncChatModule(self, self._client)
        self.models = AsyncModelsModule(self, self._client)
        self.workflows = AsyncWorkflowsModule(self, self._client)
        self.me = AsyncMeModule(self, self._client)
        self.collections = AsyncCollectionsModule(self, self._client)
        self.embeddings = AsyncEmbeddingsModule(self, self._client)
        self.documents = AsyncDocumentsModule(self, self._client)

    async def initialize(self):
        """
        Initialise le client asynchrone.
        Cette méthode est appelée pour s'assurer que le client est prêt à être utilisé.
        """
        await self._validate_api_key()
        return self

    async def _validate_api_key(self):
        """
        Valide la clé API en effectuant une requête à l'API.
        """
        try:
            await self.me.info()
        except httpx.ConnectTimeout as e:
            raise ConnectionError(
                f"Le host {self.base_url} n'est pas accessible. Vérifiez votre connexion réseau ou l'URL de l'API."
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Clé API invalide ou expirée. Veuillez vérifier votre clé API."
                ) from e
            elif e.response.status_code == 403:
                raise PermissionError(
                    "Accès interdit. Vérifiez vos permissions pour utiliser l'API."
                ) from e
            else:
                raise ValueError(
                    f"Erreur lors de la validation de la clé API: {e.response.text}"
                ) from e
        except Exception:
            raise ValueError(
                f"Clé API invalide/expirée ou le host {self.base_url} n'est pas accessible."
            )

    async def close(self):
        """
        Ferme le client.
        """
        await self._client.aclose()

    async def __aenter__(self):
        """
        Enter the context manager, returning the client instance.

        Example:
            async with AisbergAsyncClient() as client:
                # Use the client here
                pass

        Returns:
            AisbergAsyncClient: L'instance du client Aisberg.
        """
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager, closing the client.
        Example:
            async with AisbergAsyncClient() as client:
                # Use the client here
                pass
        """
        await self.close()

    def __repr__(self):
        return f"<AisbergAsyncClient base_url={self.base_url}>"

    def __str__(self):
        return f"AisbergAsyncClient(base_url={self.base_url})"
