import json
from typing import Optional, Generator, Union, List, Any, Dict

import httpx

from ..exceptions import CollectionNotFoundError, CollectionEmptyError
from ..models.chat import (
    LanguageModelInput,
    format_messages,
    ChatCompletionResponse,
    ChatCompletionChunk,
)
from ..models.collections import (
    GroupCollections,
    PointDetails,
    ParseDataInput,
)
from ..models.documents import DocumentParserResponse
from ..models.embeddings import (
    EncodingFormat,
    EncodingResponse,
    ChunksDataList,
    RerankerResponse,
)
from ..models.models import Model
from ..models.requests import AnyDict, AnyList, HttpxFileField
from ..models.token import TokenInfo
from ..models.workflows import WorkflowDetails, Workflow
from ..requests.sync_requests import req, req_stream
from ..utils import parse_chat_line, WorkflowLineParser


def models(client: httpx.Client) -> List[Model]:
    """
    Get the list of available models.
    """
    resp = req(client, "GET", "/v1/models", AnyDict).data
    if not resp or not isinstance(resp, list):
        raise ValueError("Invalid response format for models")
    return [Model.model_validate(item) for item in resp]


def workflows(client: httpx.Client) -> List[Workflow]:
    """
    Get the list of available workflows.
    """
    resp = req(client, "GET", "/workflow/light", AnyList)
    return [Workflow.model_validate(item) for item in resp.root]


def workflow(client: httpx.Client, workflow_id: str) -> WorkflowDetails:
    """
    Get details of a specific workflow.
    """
    try:
        resp = req(client, "GET", f"/workflow/details/{workflow_id}", WorkflowDetails)
        return resp
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Workflow with ID {workflow_id} not found")
        raise e


def collections(client: httpx.Client) -> List[GroupCollections]:
    """
    Get the list of available collections.
    """
    resp = req(client, "GET", "/collections", AnyList)
    return [
        GroupCollections.model_validate(
            {
                "group": item["group"],
                "collections": [{"name": name} for name in item["collections"].keys()],
            }
        )
        for item in resp.root
    ]


def collection(
    client: httpx.Client, collection_id: str, group_id: Optional[str] = None
) -> List[PointDetails]:
    """
    Get details of a specific collection.
    """
    try:
        resp = req(client, "GET", f"/collections/{collection_id}/{group_id}", AnyList)
        return [PointDetails.model_validate(item) for item in resp.root]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise CollectionNotFoundError(
                collection_name=collection_id, group_id=group_id
            ) from e
        raise e


def create_collection(
    client: httpx.Client,
    name: str,
    model: str,
    group: Optional[str] = None,
):
    """
    Create a new collection with the specified name and optional group.
    """
    payload = {"collection_name": name, "embedding_model": model}
    if group is not None:
        payload["group"] = group

    return req(
        client,
        "POST",
        "/collections",
        AnyDict,
        json=payload,
    )


def delete_collection(
    client: httpx.Client,
    name: str,
    group: Optional[str] = None,
):
    """
    Delete a collection with the specified name and optional group.
    """
    payload = {"collections": [name]}
    if group is not None:
        payload["group"] = group

    return req(
        client,
        "DELETE",
        "/collections",
        AnyDict,
        json=payload,
    )


def insert_points_in_collection(
    client: httpx.Client,
    name: str,
    files: HttpxFileField,
    normalize: bool,
    chunking_dict: Optional[Dict[str, Any]] = None,
    parse_data: Optional[ParseDataInput] = None,
    group: Optional[str] = None,
):
    """
    Insert points into a collection with the specified name.
    """
    payload = {
        "chunking_dict": json.dumps({"method": "custom", "params": {}}),
        "normalize": normalize,
    }
    if group is not None:
        payload["group"] = group

    if chunking_dict is not None:
        payload["chunking_dict"] = json.dumps(chunking_dict)

    if parse_data is not None:
        payload["parse_data"] = parse_data.model_dump_json()

    return req(
        client,
        "POST",
        f"/collections/{name}",
        AnyDict,
        data=payload,
        files=files,
    )


def delete_points_in_collection(
    client: httpx.Client,
    points_ids: List[str],
    name: str,
    group: Optional[str] = None,
):
    """
    Delete points into a collection with the specified name.
    """
    payload = {
        "points": points_ids,
        "collection": name,
    }
    if group is not None:
        payload["group"] = group

    return req(
        client,
        "DELETE",
        "/collections/chunks",
        AnyDict,
        json=payload,
    )


def delete_all_points_in_collection(
    client: httpx.Client,
    name: str,
    group: Optional[str] = None,
):
    """
    Delete All points into a collection with the specified name.
    """
    payload = {
        "collection": name,
    }
    if group is not None:
        payload["group"] = group

    return req(
        client,
        "DELETE",
        "/collections/all/chunks",
        AnyDict,
        json=payload,
    )


def me(client: httpx.Client) -> TokenInfo:
    """
    Get the details of the current user.
    """
    return req(client, "GET", "/users/me", TokenInfo)


def chat(
    client: httpx.Client,
    input: LanguageModelInput,
    model: str = None,
    temperature: float = 0.7,
    group: Optional[str] = None,
    **kwargs,
) -> ChatCompletionResponse:
    """
    Send a chat message and get a response from an LLM endpoint.
    """
    if model is None:
        raise ValueError("Model must be specified")

    formatted_messages = format_messages(input)

    payload = {
        "model": model,
        "messages": formatted_messages,
        "temperature": temperature,
        "stream": False,
        **kwargs,
    }

    if group is not None:
        payload["group"] = group

    return req(
        client,
        "POST",
        "/v1/chat/completions",
        ChatCompletionResponse,
        json=payload,
    )


def stream(
    client: httpx.Client,
    input: LanguageModelInput,
    model: str,
    temperature: float = 0.7,
    full_chunk: bool = True,
    group: Optional[str] = None,
    **kwargs,
) -> Generator[Union[str, ChatCompletionChunk, ChatCompletionResponse], None, None]:
    """
    Stream de complétions OpenAI.
    - Si `full_chunk` est True (défaut) : chaque yield est le JSON complet du chunk.
    - Sinon : on garde la compat ascendante → on ne yield que le delta.content + marquages.
    """
    formatted_messages = format_messages(input)

    payload = {
        "model": model,
        "messages": formatted_messages,
        "temperature": temperature,
        "stream": True,
        **kwargs,
    }

    if group is not None:
        payload["group"] = group

    for chunk in req_stream(
        client,
        "POST",
        "/v1/chat/completions",
        parse_line=lambda line: parse_chat_line(line, full_chunk=full_chunk),
        json=payload,
    ):
        if chunk is None:
            continue

        yield chunk


def embeddings(
    client: httpx.Client,
    input: str,
    model: str,
    encoding_format: EncodingFormat,
    normalize: bool,
    group: Optional[str] = None,
    **kwargs,
) -> EncodingResponse:
    """
    Get embeddings for a given input using the specified model.
    """
    payload = {
        "model": model,
        "input": input,
        "encoding_format": encoding_format,
        "normalize": normalize,
        **kwargs,
    }

    if group is not None:
        payload["group"] = group

    return req(
        client,
        "POST",
        "/v1/embeddings",
        EncodingResponse,
        json=payload,
    )


def retrieve(
    client: httpx.Client,
    query: str,
    collections_names: List[str],
    limit: int,
    score_threshold: float,
    filters: list,
    beta: float,
    group: Optional[str] = None,
    **kwargs,
) -> ChunksDataList:
    """
    Retrieve the most relevant documents based on the given query from specified collections.
    """
    data = {
        "query": query,
        "collections_names": collections_names,
        "limit": limit,
        "score": score_threshold,
        "filters": filters,
        "beta": beta,
        **kwargs,
    }

    if group is not None:
        data["group"] = group

    try:
        return req(
            client,
            "POST",
            "/collections/run/search",
            ChunksDataList,
            json=data,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            if "list index out of range" in str(e.response.text):
                raise CollectionEmptyError(
                    collection_name="/".join(collections_names),
                    group_id=group,
                ) from e

        raise e


def rerank(
    client: httpx.Client,
    query: str,
    documents: List[str],
    model: str,
    top_n: int,
    return_documents: bool,
    group: Optional[str] = None,
    **kwargs,
) -> RerankerResponse:
    """
    Rerank a list of documents based on their relevance to a given query using the specified model.
    """
    payload = {
        "query": query,
        "documents": documents,
        "model": model,
        "top_n": top_n,
        "return_documents": return_documents,
        **kwargs,
    }

    if group is not None:
        payload["group"] = group

    return req(
        client,
        "POST",
        "/v1/rerank",
        RerankerResponse,
        json=payload,
    )


def run_workflow(
    client: httpx.Client,
    workflow_id: str,
    data: dict,
) -> Any:
    """
    Run a specific workflow with the provided data.
    """
    try:
        parser = WorkflowLineParser()
        for chunk in req_stream(
            client,
            "POST",
            f"/workflow/run/{workflow_id}",
            parse_line=parser,
            json=data,
        ):
            yield chunk
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Workflow with ID {workflow_id} not found")
        raise e


def parse_documents(
    client: httpx.Client,
    files: HttpxFileField,
    group: Optional[str] = None,
    **kwargs,
) -> DocumentParserResponse:
    """
    Parse a single or multiple documents using the document parser endpoint.
    Returns the content of the parsed documents.
    """
    payload = {**kwargs}
    if group is not None:
        payload["group"] = group

    response = req(
        client,
        "POST",
        "/document-parser/parsing/parse",
        DocumentParserResponse,
        files=files,
        data=payload,
    )
    return response
