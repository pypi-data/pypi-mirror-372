from typing import Dict, Callable

import httpx

from .config import settings
from .modules import (
    SyncChatModule,
    SyncCollectionsModule,
    SyncEmbeddingsModule,
    SyncMeModule,
    SyncModelsModule,
    SyncWorkflowsModule,
    ToolsModule,
    SyncDocumentsModule,
)


class AisbergClient:
    def __init__(self, base_url=None, api_key=None, timeout=None):
        self.api_key = api_key or settings.aisberg_api_key
        self.base_url = base_url or settings.aisberg_base_url
        self.timeout = (
            timeout or settings.aisberg_timeout
        )  # default to 180 seconds (3 minutes)

        if not self.base_url or not self.api_key:
            raise ValueError(
                "L'URL de base et la clé API doivent être définies. "
                "Utilisez les variables d'environnement AISBERG_API_KEY et AISBERG_BASE_URL ou passez-les lors de l'initialisation du client."
            )

        self.tool_registry: Dict[str, Callable] = {}
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        # Modules
        self.tools = ToolsModule(self)
        self.chat = SyncChatModule(self, self._client)
        self.models = SyncModelsModule(self, self._client)
        self.workflows = SyncWorkflowsModule(self, self._client)
        self.me = SyncMeModule(self, self._client)
        self.collections = SyncCollectionsModule(self, self._client)
        self.embeddings = SyncEmbeddingsModule(self, self._client)
        self.documents = SyncDocumentsModule(self, self._client)

        # Validate API key
        self._validate_api_key()

    def _validate_api_key(self):
        """
        Valide la clé API en effectuant une requête à l'API.
        """
        try:
            self.me.info()
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
        except Exception as e:
            raise ValueError(
                f"Clé API invalide/expirée ou le host {self.base_url} n'est pas accessible. Erreur: {str(e)}"
            )

    def close(self):
        """
        Ferme le client.
        """
        self._client.close()

    def __enter__(self):
        """
        Enter the context manager, returning the client instance.

        Example:
            with AisbergClient() as client:
                # Use the client here
                pass

        Returns:
            AisbergClient: L'instance du client Aisberg.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager, closing the client.
        Example:
            with AisbergClient() as client:
                # Use the client here
                pass
        """
        self.close()

    def __repr__(self):
        return f"<AisbergClient base_url={self.base_url}>"

    def __str__(self):
        return f"AisbergClient(base_url={self.base_url})"
