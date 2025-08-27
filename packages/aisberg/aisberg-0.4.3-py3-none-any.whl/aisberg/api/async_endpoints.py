import json
from typing import Optional, AsyncGenerator, Union, List, Any, Dict

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
from ..requests.async_requests import areq, areq_stream
from ..utils import parse_chat_line, WorkflowLineParser


async def models(client: httpx.AsyncClient) -> List[Model]:
    """
    Get the list of available models.
    """
    resp = await areq(client, "GET", "/v1/models", AnyDict)
    data = resp.data
    if not data or not isinstance(data, list):
        raise ValueError("Invalid response format for models")
    return [Model.model_validate(item) for item in data]


async def workflows(client: httpx.AsyncClient) -> List[Workflow]:
    """
    Get the list of available workflows.
    """
    resp = await areq(client, "GET", "/workflow/light", AnyList)
    return [Workflow.model_validate(item) for item in resp.root]


async def workflow(client: httpx.AsyncClient, workflow_id: str) -> WorkflowDetails:
    """
    Get details of a specific workflow.
    """
    try:
        resp = await areq(
            client, "GET", f"/workflow/details/{workflow_id}", WorkflowDetails
        )
        return resp
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Workflow with ID {workflow_id} not found")
        raise e


async def collections(client: httpx.AsyncClient) -> List[GroupCollections]:
    """
    Get the list of available collections.
    """
    resp = await areq(client, "GET", "/collections", AnyList)
    return [
        GroupCollections.model_validate(
            {
                "group": item["group"],
                "collections": [{"name": name} for name in item["collections"].keys()],
            }
        )
        for item in resp.root
    ]


async def collection(
    client: httpx.AsyncClient, collection_id: str, group_id: Optional[str] = None
) -> List[PointDetails]:
    """
    Get details of a specific collection.
    """
    try:
        resp = await areq(
            client, "GET", f"/collections/{collection_id}/{group_id}", AnyList
        )
        return [PointDetails.model_validate(item) for item in resp.root]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise CollectionNotFoundError(
                collection_name=collection_id, group_id=group_id
            ) from e
        raise e


async def create_collection(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "POST",
        "/collections",
        AnyDict,
        json=payload,
    )


async def delete_collection(
    client: httpx.AsyncClient,
    name: str,
    group: Optional[str] = None,
):
    """
    Delete a collection with the specified name and optional group.
    """
    payload = {"collections": [name]}
    if group is not None:
        payload["group"] = group

    return await areq(
        client,
        "DELETE",
        "/collections",
        AnyDict,
        json=payload,
    )


async def insert_points_in_collection(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "POST",
        f"/collections/{name}",
        AnyDict,
        data=payload,
        files=files,
    )


async def delete_points_in_collection(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "DELETE",
        "/collections/chunks",
        AnyDict,
        json=payload,
    )


async def delete_all_points_in_collection(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "DELETE",
        "/collections/all/chunks",
        AnyDict,
        json=payload,
    )


async def me(client: httpx.AsyncClient) -> TokenInfo:
    """
    Get the details of the current user.
    """
    return await areq(client, "GET", "/users/me", TokenInfo)


async def chat(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "POST",
        "/v1/chat/completions",
        ChatCompletionResponse,
        json=payload,
    )


async def chat_stream(
    client: httpx.AsyncClient,
    input: LanguageModelInput,
    model: str,
    temperature: float = 0.7,
    full_chunk: bool = True,
    group: Optional[str] = None,
    **kwargs,
) -> AsyncGenerator[Union[str, ChatCompletionChunk], None]:
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

    async for chunk in areq_stream(
        client,
        "POST",
        "/v1/chat/completions",
        parse_line=lambda line: parse_chat_line(line, full_chunk=full_chunk),
        json=payload,
    ):
        if chunk is None:
            continue

        yield chunk


async def embeddings(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "POST",
        "/v1/embeddings",
        EncodingResponse,
        json=payload,
    )


async def retrieve(
    client: httpx.AsyncClient,
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
        return await areq(
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


async def rerank(
    client: httpx.AsyncClient,
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

    return await areq(
        client,
        "POST",
        "/v1/rerank",
        RerankerResponse,
        json=payload,
    )


async def run_workflow(
    client: httpx.AsyncClient,
    workflow_id: str,
    data: dict,
) -> Any:
    """
    Run a specific workflow with the provided data.
    """
    try:
        parser = WorkflowLineParser()
        async for chunk in areq_stream(
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


async def parse_documents(
    client: httpx.AsyncClient,
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

    response = await areq(
        client,
        "POST",
        "/document-parser/parsing/parse",
        DocumentParserResponse,
        files=files,
        data=payload,
    )
    return response
