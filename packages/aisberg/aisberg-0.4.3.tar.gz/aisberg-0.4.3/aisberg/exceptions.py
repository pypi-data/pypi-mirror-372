class APIError(Exception):
    pass


class AuthError(APIError):
    pass


class ToolExecutionError(Exception):
    """Exception levée lors de l'exécution d'un tool"""

    pass


class ToolNotFoundError(Exception):
    """Exception levée lorsqu'un tool n'est pas trouvé"""

    def __init__(self, tool_name: str):
        super().__init__(f"Tool '{tool_name}' not found.")
        self.tool_name = tool_name


class UnspecifiedClassArgumentError(Exception):
    """Exception levée lorsqu'un argument requis n'est pas spécifié"""

    def __init__(self, argument_name: str):
        super().__init__(
            f"L'argument '{argument_name}' est requis mais n'a pas été spécifié."
        )
        self.argument_name = argument_name


class CollectionNotFoundError(Exception):
    """Exception levée lorsqu'une collection n'est pas trouvée"""

    def __init__(self, collection_name: str, group_id: str):
        super().__init__(
            f"La collection '{collection_name}' dans le groupe '{group_id}' n'a pas été trouvée."
        )
        self.collection_name = collection_name
        self.group_id = group_id


class CollectionEmptyError(Exception):
    """Exception levée lorsqu'une collection est vide"""

    def __init__(self, collection_name: str, group_id: str):
        super().__init__(
            f"La collection '{collection_name}' dans le groupe '{group_id}' est vide."
        )
        self.collection_name = collection_name
        self.group_id = group_id
