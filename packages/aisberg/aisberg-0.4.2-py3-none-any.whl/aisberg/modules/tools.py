from typing import Callable, Dict, Any

from ..abstract.modules import BaseModule
from ..exceptions import ToolExecutionError, ToolNotFoundError


class ToolsModule(BaseModule):
    """
    Tools module for the aisberg application.
    This module provides methods to register and execute tools.
    """

    def __init__(self, parent):
        """
        Initialize the ToolsModule.

        Args:
            parent (AisbergClient): Parent client instance.
        """
        super().__init__(parent)

    def register(self, name: str, func: Callable) -> None:
        """
        Enregistre une fonction comme tool disponible.

        Args:
            name (str): Nom du tool (doit correspondre au nom dans la définition du tool)
            func (Callable): Fonction à exécuter quand le tool est appelé
        """
        self._parent.tool_registry[name] = func

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Exécute un tool avec les arguments fournis.

        Args:
            tool_name (str): Nom du tool à exécuter
            arguments (Dict[str, Any]): Arguments à passer au tool

        Returns:
            Any: Résultat de l'exécution du tool

        Raises:
            ToolExecutionError: Si le tool n'existe pas ou si l'exécution échoue
        """
        if tool_name not in self._parent.tool_registry:
            raise ToolNotFoundError(tool_name=tool_name)

        try:
            return self._parent.tool_registry[tool_name](**arguments)
        except Exception as e:
            raise ToolExecutionError(f"Error executing tool '{tool_name}': {str(e)}")

    def list(self) -> Dict[str, Callable]:
        """
        Liste tous les tools enregistrés.

        Returns:
            Dict[str, Callable]: Dictionnaire des tools enregistrés avec leur nom et fonction
        """
        return self._parent.tool_registry

    def clear(self) -> None:
        """
        Efface tous les tools enregistrés.
        """
        self._parent.tool_registry.clear()

    def remove(self, tool_name: str) -> None:
        """
        Supprime un tool enregistré.

        Args:
            tool_name (str): Nom du tool à supprimer
        """
        if tool_name in self._parent.tool_registry:
            del self._parent.tool_registry[tool_name]
        else:
            raise ToolNotFoundError(tool_name=tool_name)
