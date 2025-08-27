import warnings
from enum import Enum
from typing import Union, Sequence, Tuple, Dict, Any, List, Optional, Literal

from pydantic import BaseModel, Field, model_validator


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: "FunctionCall"


class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON string des arguments


class BaseMessage(BaseModel):
    role: RoleEnum
    content: Union[str, None]


class HumanMessage(BaseMessage):
    role: RoleEnum = Field(default=RoleEnum.user, frozen=True)


class AIMessage(BaseMessage):
    role: RoleEnum = Field(default=RoleEnum.assistant, frozen=True)
    tool_calls: Optional[List[ToolCall]] = None


class SystemMessage(BaseMessage):
    role: RoleEnum = Field(default=RoleEnum.system, frozen=True)


class ToolMessage(BaseMessage):
    role: RoleEnum = Field(default=RoleEnum.tool, frozen=True)
    tool_call_id: str  # ID du tool_call auquel ce message répond


# Types de représentations acceptées comme "message"
MessageLikeRepresentation = Union[
    BaseMessage,  # BaseMessage ou ses sous-classes
    str,  # Simple string message
    Tuple[str, str],  # (role, content)
    Dict[str, Any],  # dict style {"role": "user", "content": "..."}
]

# Entrée possible pour un LLM
LanguageModelInput = Union[str, Sequence[MessageLikeRepresentation]]


class ChatMessageContent(BaseModel):
    role: str
    content: Optional[str] = ""
    refusal: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None
    function_call: Optional[FunctionCall] = None
    tool_calls: Optional[List[ToolCall]] = None
    reasoning_content: Optional[str] = None


class DeltaToolCallFunction(BaseModel):
    """Représente la fonction dans un delta de tool_call."""

    name: Optional[str] = None
    arguments: Optional[str] = None


class DeltaToolCall(BaseModel):
    """Représente un delta de tool_call individuel avec un typage fort."""

    index: int
    id: Optional[str] = None
    function: DeltaToolCallFunction = Field(default_factory=DeltaToolCallFunction)
    type: Optional[str] = "function"


class Delta(BaseModel):
    content: Optional[str] = ""
    reasoning_content: Optional[str] = None
    function_call: Optional[dict] = None
    tool_calls: Optional[List[DeltaToolCall]] = None


class ChatChoice(BaseModel):
    index: int
    message: ChatMessageContent
    finish_reason: Optional[str]


class ChoiceChunk(BaseModel):
    index: int
    delta: Delta
    finish_reason: Optional[str]


class ChatUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Optional[ChatUsage] = None
    warning: Optional[str] = None

    @model_validator(mode="after")
    def check_for_warning(self):
        if self.warning:
            warnings.warn(f"[ChatCompletionResponse] {self.warning}")
        return self


class ChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"]
    created: int
    model: str
    choices: List[ChoiceChunk]
    usage: Optional[ChatUsage] = None
    warning: Optional[str] = None

    @model_validator(mode="after")
    def check_for_warning(self):
        if self.warning:
            warnings.warn(f"[ChatCompletionChunk] {self.warning}")
        return self


def parse_message(msg: MessageLikeRepresentation) -> BaseMessage:
    if isinstance(msg, BaseMessage):
        return msg
    elif isinstance(msg, HumanMessage):
        return msg
    elif isinstance(msg, AIMessage):
        return msg
    elif isinstance(msg, SystemMessage):
        return msg
    elif isinstance(msg, ToolMessage):
        return msg
    elif isinstance(msg, str):
        return HumanMessage(content=msg)
    elif isinstance(msg, tuple) and len(msg) == 2:
        return BaseMessage(role=RoleEnum(msg[0]), content=msg[1])
    elif isinstance(msg, dict):
        return BaseMessage(**msg)
    else:
        raise ValueError(f"Invalid message representation: {msg}")


def format_messages(input: LanguageModelInput) -> list[dict]:
    """
    Normalise et formate les messages pour l’API LLM (OpenAI-like).
    """
    if isinstance(input, str):
        messages = [HumanMessage(content=input)]
    else:
        messages = [parse_message(msg) for msg in input]
    return [
        msg.model_dump(
            include={"role", "content", "tool_calls", "tool_call_id"}, exclude_none=True
        )
        for msg in messages
    ]
