from typing import Dict, List, Optional, Iterable, Union

from pydantic import BaseModel, Field


class Property(BaseModel):
    type: str = Field(..., description="e.g., string, number, boolean, array, object")
    description: str
    enum: Optional[List[str]] = None


class Parameters(BaseModel):
    type: str = Field("object", frozen=True)
    properties: Dict[str, Property]
    required: Optional[List[str]] = None


class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(BaseModel):
    type: str = Field("function", frozen=True)
    function: Function


def make_tool(
    *,
    name: str,
    description: str,
    parameters: Dict[str, Dict[str, Union[str, List[str]]]],
    required: Optional[List[str]] = None,
) -> Tool:
    """
    Creates a `Tool` object compatible with the OpenAI API.

    Args:
        name: Name of the function.
        description: Description of the function.
        parameters: Dictionary describing each parameter.
            Format: {“param_name”: {“type”: “string”, ‘description’: “...”, “enum”: [...]}}
            Supported types: string, number, boolean, array, object
        required: List of required parameters. If omitted, all parameters are required by default.

    Returns:
        A `Tool` object compliant with OpenAI.
    """
    props = {}
    for key, config in parameters.items():
        props[key] = Property(
            type=config["type"],
            description=config["description"],
            enum=config.get("enum"),
        )

    return Tool(
        function=Function(
            name=name,
            description=description,
            parameters=Parameters(
                type="object",
                properties=props,
                required=required
                or list(parameters.keys()),  # by default all are required
            ),
        )
    )


def tools_to_payload(tools: Iterable[Tool]) -> List[Dict]:
    """
    Convert `Tool` objects in JSON payloads compatible with OpenAI API format.
    """
    if not tools:
        return []

    if not isinstance(tools, Iterable):
        raise ValueError("tools must be an iterable")

    return [tool.model_dump(mode="json", exclude_none=True) for tool in tools]
