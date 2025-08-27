from abc import ABC, abstractmethod
from typing import Optional, Union, List, Literal

from ..abstract.modules import AsyncModule, SyncModule
from ..api import async_endpoints, endpoints
from ..models.collections import Collection
from ..models.embeddings import (
    EncodingResponse,
    ChunksDataList,
    RerankerResponse,
    ChunkData,
)


class AbstractEmbeddingsModule(ABC):
    """
    Abstract base class for embeddings modules.
    Handles common logic for embedding operations across synchronous and asynchronous modules.
    """

    def __init__(self, parent, http_client):
        """
        Initialize the AbstractEmbeddingsModule.

        Args:
            parent: Parent client instance.
            http_client: HTTP client for making requests.
        """
        self._parent = parent
        self._client = http_client

    @abstractmethod
    def encode(
        self,
        input: str,
        model: str,
        encoding_format: Optional[Literal["float", "base64"]] = "float",
        normalize: Optional[bool] = False,
        **kwargs,
    ) -> EncodingResponse:
        """Encode a list of texts into embeddings.

        Args:
            input (str): The text or texts to encode. Can be a single string or a list of strings.
            model (str): The model to use for encoding. Defaults to "text-embedding-3-small".
            encoding_format (str): The format of the encoding. Defaults to "float". Can be "float" or "base64".
            normalize (bool): Whether to normalize the embeddings. Defaults to False.
            **kwargs: Additional parameters for the encoding.

        Returns:
            EncodingResponse: The response containing the encoded embeddings.
        """
        ...

    @abstractmethod
    def retrieve(
        self,
        query: str,
        collections_names: List[Union[str, Collection]],
        limit: int = 10,
        score_threshold: float = 0.0,
        filters: List = None,
        beta: float = 0.7,
    ) -> ChunksDataList:
        """Retrieve similar texts based on a query.

        Args:
            query (str): The query text to retrieve similar texts for.
            collections_names (List[str]): A list of collection names to search in.
            limit (int): The maximum number of results to return. Defaults to 10.
            score_threshold (float): The minimum score threshold for results. Defaults to 0.0.
            filters (list): A list of filters to apply to the retrieval.
            beta (float): Dense/Sparse trade-off parameter. Defaults to 0.7. 0 means full sparse, 1 means full dense.

        Returns:
            List[ChunkData]: A list of ChunkData objects containing the retrieved texts and their metadata.
        """
        ...

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: Union[ChunksDataList, List[Union[str, ChunkData]]],
        model: str,
        top_n: int = 10,
        return_documents: bool = True,
        threshold: Optional[float] = None,
    ) -> RerankerResponse:
        """Rerank texts based on a query.

        Args:
            query (str): The query text to rerank the documents against.
            documents (Union[ChunksDataList, List[Union[str, ChunkData]]]): A list of documents to rerank. Can be a ChunksDataList or a list of strings or ChunkData objects.
            model (str): The model to use for reranking. Defaults to "text-embedding-3-small".
            top_n (int): The number of top results to return. Defaults to 10.
            return_documents (bool): Whether to return the original documents in the response. Defaults to True.
            threshold (Optional[float]): A threshold for filtering results. If provided, only results with a score above this threshold will be returned. Defaults to None.

        Returns:
            RerankerResponse: The response containing the reranked documents and their scores.

        Raises:
            ValueError: If the documents list is empty or contains invalid document types.
            Exception: If the documents list is not of the expected type.
        """
        ...

    @staticmethod
    def _format_collections_names(
        collections_names: List[Union[str, Collection]],
    ) -> List[str]:
        """Format the input collections names into a list of strings."""
        coll_names = []

        for coll in collections_names:
            if isinstance(coll, Collection):
                coll_names.append(coll.name)
            elif isinstance(coll, str):
                coll_names.append(coll)
            else:
                raise ValueError(
                    f"Invalid collection type: {type(coll)}. Expected str or Collection."
                )

        return coll_names

    @staticmethod
    def _format_chunks_data_list(
        documents: Union[ChunksDataList, List[Union[str, ChunkData]]],
    ) -> List[str]:
        """Format the input documents into a ChunksDataList."""
        chunks = []

        if isinstance(documents, ChunksDataList):
            chunks = documents.texts()
        elif isinstance(documents, list):
            if len(documents) == 0:
                raise ValueError("Documents list is empty.")

            for doc in documents:
                if isinstance(doc, ChunkData):
                    chunks.append(doc.text)
                elif isinstance(doc, str):
                    chunks.append(doc)
                else:
                    raise ValueError(
                        f"Invalid document type: {type(doc)}. Expected str or ChunkData."
                    )
        else:
            raise Exception(
                f"Documents list is not of the expected type: {type(documents)}. Expected ChunksDataList or list of str or ChunkData."
            )

        return chunks


class SyncEmbeddingsModule(AbstractEmbeddingsModule, SyncModule):
    """
    `SyncEmbeddingsModule` is a synchronous module that provides a high-level interface for interacting with
    embeddings tools. The module abstracts all communication with the backend API,
    providing both blocking and generator-based usage.
    """

    def __init__(self, parent, http_client):
        super().__init__(parent, http_client)
        SyncModule.__init__(self, parent, http_client)

    def encode(
        self,
        input: str,
        model: str,
        encoding_format: Optional[Literal["float", "base64"]] = "float",
        normalize: Optional[bool] = False,
        **kwargs,
    ) -> EncodingResponse:
        resp = endpoints.embeddings(
            self._client,
            input=input,
            model=model,
            encoding_format=encoding_format,
            normalize=normalize,
            **kwargs,
        )
        return EncodingResponse.model_validate(resp)

    def retrieve(
        self,
        query: str,
        collections_names: List[Union[str, Collection]],
        limit: int = 10,
        score_threshold: float = 0.0,
        filters: List = None,
        beta: float = 0.7,
        **kwargs,
    ) -> ChunksDataList:
        if filters is None:
            filters = []

        resp = endpoints.retrieve(
            self._client,
            query=query,
            collections_names=self._format_collections_names(collections_names),
            limit=limit,
            score_threshold=score_threshold,
            filters=filters,
            beta=beta,
            **kwargs,
        )
        return ChunksDataList.model_validate(resp)

    def rerank(
        self,
        query: str,
        documents: Union[ChunksDataList, List[Union[str, ChunkData]]],
        model: str,
        top_n: int = 10,
        return_documents: bool = True,
        threshold: Optional[float] = None,
        **kwargs,
    ) -> RerankerResponse:
        resp = endpoints.rerank(
            self._client,
            query,
            self._format_chunks_data_list(documents),
            model,
            top_n,
            return_documents,
            **kwargs,
        )
        resp = RerankerResponse.model_validate(resp)

        if threshold is not None:
            resp = resp.filter_by_relevance_score(threshold)

        return resp


class AsyncEmbeddingsModule(AbstractEmbeddingsModule, AsyncModule):
    """
    `AsyncEmbeddingsModule` is an asynchronous module that provides a high-level interface for interacting with
    embeddings tools. The module abstracts all communication with the backend API,
    providing both blocking and generator-based usage.
    """

    def __init__(self, parent, http_client):
        super().__init__(parent, http_client)
        AsyncModule.__init__(self, parent, http_client)

    async def encode(
        self,
        input: str,
        model: str,
        encoding_format: Optional[Literal["float", "base64"]] = "float",
        normalize: Optional[bool] = False,
        **kwargs,
    ) -> EncodingResponse:
        resp = await async_endpoints.embeddings(
            self._client,
            input=input,
            model=model,
            encoding_format=encoding_format,
            normalize=normalize,
            **kwargs,
        )
        return EncodingResponse.model_validate(resp)

    async def retrieve(
        self,
        query: str,
        collections_names: List[Union[str, Collection]],
        limit: int = 10,
        score_threshold: float = 0.0,
        filters: List = None,
        beta: float = 0.7,
        **kwargs,
    ) -> ChunksDataList:
        if filters is None:
            filters = []

        resp = await async_endpoints.retrieve(
            self._client,
            query=query,
            collections_names=self._format_collections_names(collections_names),
            limit=limit,
            score_threshold=score_threshold,
            filters=filters,
            beta=beta,
            **kwargs,
        )
        return ChunksDataList.model_validate(resp)

    async def rerank(
        self,
        query: str,
        documents: Union[ChunksDataList, List[Union[str, ChunkData]]],
        model: str,
        top_n: int = 10,
        return_documents: bool = True,
        threshold: Optional[float] = None,
        **kwargs,
    ) -> RerankerResponse:
        resp = await async_endpoints.rerank(
            self._client,
            query,
            self._format_chunks_data_list(documents),
            model,
            top_n,
            return_documents,
            **kwargs,
        )
        resp = RerankerResponse.model_validate(resp)

        if threshold is not None:
            resp = resp.filter_by_relevance_score(threshold)

        return resp
