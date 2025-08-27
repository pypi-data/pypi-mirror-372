import json
import os
from abc import ABC
from abc import abstractmethod
from io import BytesIO
from typing import List, Union, Optional, Dict, Any

from ..abstract.modules import SyncModule, AsyncModule
from ..api import endpoints, async_endpoints
from ..models.collections import (
    GroupCollections,
    Collection,
    CollectionDetails,
    CollectionDataset,
    ParseDataInput,
    ChunkingMethod,
    resolve_chunking_dict,
)
from ..models.requests import HttpxFileField


class AbstractCollectionsModule(ABC):
    def __init__(self, parent, client):
        self._parent = parent
        self._client = client

    @abstractmethod
    def list(self) -> List[GroupCollections]:
        """
        Get a list of available collections. Collections are grouped by your belonging groups.

        Returns:
            List[GroupCollections]: A list of available collections.

        Raises:
            ValueError: If no collections are found.
            Exception: If there is an error fetching the collections.
        """
        ...

    @abstractmethod
    def get_by_group(self, group_id: str) -> List[Collection]:
        """
        Get collections by group ID.

        Args:
            group_id (str): The ID of the group for which to retrieve collections.

        Returns:
            List[Collection]: A list of collections for the specified group.

        Raises:
            ValueError: If no collections are found for the specified group ID.
            Exception: If there is an error fetching the collections.
        """
        ...

    @abstractmethod
    def details(self, collection_id: str, group_id: str) -> CollectionDetails:
        """
        Get details of a specific collection.

        Args:
            collection_id (str): The ID of the collection to retrieve.
            group_id (str): The ID of the group to which the collection belongs.

        Returns:
            CollectionDetails: The details of the specified collection.

        Raises:
            ValueError: If the specified collection is not found.
        """
        ...

    @abstractmethod
    def delete(self, name: str, **kwargs) -> bool:
        """
        Delete a collection by name and group ID.

        Args:
            name (str): The name of the collection to delete.
            **kwargs: Additional keyword arguments, such as group ID.

        Returns:
            bool: True if the deletion was successful, False otherwise.

        Raises:
            ValueError: If the collection could not be deleted.
            Exception: If there is an error during the deletion process.
        """
        ...

    @abstractmethod
    def create(
        self,
        name: str,
        data: Optional[Union[dict, CollectionDataset, str]] = None,
        embedding_model: Optional[str] = "BAAI/bge-m3",
        normalize: bool = False,
        chunking_method: ChunkingMethod = "custom",
        chunking_dict: Optional[Dict[str, Any]] = None,
        parse_data: Optional[ParseDataInput] = None,
        **kwargs,
    ) -> CollectionDetails:
        """
        Create a new collection.

        Args:
            name (str): The name of the collection to create.
            data (Union[dict, CollectionDataset, str]): The data to insert into the collection.
                Can be a Dict, aCollectionDataset object or a string representing the file path.
            embedding_model (Optional[str]): The embedding model to use for the collection.
                Defaults to "BAAI/bge-m3".
            normalize (bool): Whether to normalize the data before inserting it into the collection. Defaults to False.
            chunking_method (ChunkingMethod): The chunking method to use to chunk data
            chunking_dict (Optional[Dict[str, Any]]): Optional chunking dictionary input for the collection if applicable.
            parse_data (Optional[ParseDataInput]): Optional input for parsing data, such as source, diarization, and models.
            **kwargs: Additional keyword arguments, such as group ID.

        Returns:
            CollectionDetails: The details of the created collection.
        Raises:
            ValueError: If the collection could not be created.
            Exception: If there is an error during the creation process.
        """
        ...

    @abstractmethod
    def insert_points(
        self,
        collection_name: str,
        data: Union[dict, CollectionDataset, str],
        normalize: bool = False,
        chunking_method: ChunkingMethod = "custom",
        chunking_dict: Optional[Dict[str, Any]] = None,
        parse_data: Optional[ParseDataInput] = None,
        **kwargs,
    ) -> CollectionDetails:
        """
        Insert points into an existing collection. All existing points in the collection won't be deleted.
        This method is used to add new data to an existing collection without removing the previous data.

        Args:
            collection_name (str): The name of the collection to create.
            data (Union[dict, CollectionDataset, str]): The data to insert into the collection.
                Can be a Dict, aCollectionDataset object or a string representing the file path.
            normalize (bool): If collection already have points, the normalize parameter will be ignored. Defaults to False.
            chunking_method (ChunkingMethod): The chunking method to use to chunk data
            chunking_dict (Optional[Dict[str, Any]]): Optional chunking dictionary input for the collection if applicable.
            parse_data (Optional[ParseDataInput]): Optional input for parsing data, such as source, diarization, and models.
            **kwargs: Additional keyword arguments, such as group ID.

        Returns:
            CollectionDetails: The details of the created collection.
        Raises:
            ValueError: If the collection could not be created.
            Exception: If there is an error during the creation process.
        """
        ...

    @abstractmethod
    def delete_points(
        self,
        collection_name: str,
        points: List[str],
        **kwargs,
    ) -> CollectionDetails:
        """
        Delete points into an existing collection. Points with the specified IDs will be removed from the collection.

        Args:
            collection_name (str): The name of the collection to create.
            points (List[str]): The list of point IDs to delete from the collection.
            **kwargs: Additional keyword arguments, such as group ID.

        Returns:
            CollectionDetails: The details of the created collection.
        Raises:
            ValueError: If the collection could not be created.
            Exception: If there is an error during the creation process.
        """
        ...

    @abstractmethod
    def clear(
        self,
        collection_name: str,
        **kwargs,
    ) -> CollectionDetails:
        """
        Delete ALL points into an existing collection. All points will be removed from the collection. But the collection itself will not be deleted.
        So you will still be able to insert new points into the collection without creating a new one.

        Args:
            collection_name (str): The name of the collection to create.
            **kwargs: Additional keyword arguments, such as group ID.

        Returns:
            CollectionDetails: The details of the created collection.
        Raises:
            ValueError: If the collection could not be created.
            Exception: If there is an error during the creation process.
        """
        ...

    @staticmethod
    def _get_collections_by_group(
        collections: List[GroupCollections], group_id: str
    ) -> List[Collection]:
        for group in collections:
            if group.group == group_id:
                return group.collections
        raise ValueError("No collections found for group ID")

    @staticmethod
    def _data_to_httpx_file(
        data: Union[dict, CollectionDataset, str],
    ) -> HttpxFileField:
        """
        Prepare a payload as a HTTPX file field (for multipart upload).

        Args:
            data (dict | CollectionDataset | str): The dataset as dict/obj or a path to a JSON file.

        Returns:
            HttpxFileField: List suitable for HTTPX multipart upload.
        """
        buffer = BytesIO()
        mime_type = "application/octet-stream"

        if isinstance(data, str):
            filename = os.path.basename(data)
            with open(data, "r", encoding="utf-8") as f:
                content = f.read()
                buffer.write(content.encode("utf-8"))
            if filename.endswith(".json"):
                mime_type = "application/json"

        elif isinstance(data, CollectionDataset):
            coll_dict = data.model_dump()
            buffer.write(json.dumps(coll_dict, ensure_ascii=False).encode("utf-8"))
            filename = "collection.json"
            mime_type = "application/json"

        elif isinstance(data, dict):
            if "chunks" in data and "metadata" in data:
                buffer.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
                filename = "collection.json"
                mime_type = "application/json"
            else:
                raise ValueError(
                    "data must be a dict with 'chunks' and 'metadata' keys"
                )
        else:
            raise ValueError(
                "data must be a dict, CollectionDataset, or file path string"
            )

        buffer.seek(0)  # Reset the buffer position to the beginning
        file_tuple = ("files", (filename, buffer, mime_type))
        return [file_tuple]


class SyncCollectionsModule(SyncModule, AbstractCollectionsModule):
    def __init__(self, parent, client):
        SyncModule.__init__(self, parent, client)
        AbstractCollectionsModule.__init__(self, parent, client)

    def list(self) -> List[GroupCollections]:
        return endpoints.collections(self._client)

    def get_by_group(self, group_id: str) -> List[Collection]:
        collections = self.list()
        return self._get_collections_by_group(collections, group_id)

    def details(
        self, collection_id: str, group_id: Optional[str] = None
    ) -> CollectionDetails:
        points = endpoints.collection(self._client, collection_id, group_id)
        return CollectionDetails(
            name=collection_id,
            group=group_id,
            points=points if points else [],
        )

    def delete(self, name: str, **kwargs) -> bool:
        response = endpoints.delete_collection(self._client, name, **kwargs)
        if response is None:
            raise ValueError("Collection could not be deleted")
        return True

    def create(
        self,
        name: str,
        data: Optional[Union[dict, CollectionDataset, str]] = None,
        embedding_model: Optional[str] = "BAAI/bge-m3",
        normalize: bool = False,
        chunking_method: ChunkingMethod = "custom",
        chunking_dict: Optional[Dict[str, Any]] = None,
        parse_data: Optional[ParseDataInput] = None,
        **kwargs,
    ) -> CollectionDetails:
        create = endpoints.create_collection(
            self._client, name, embedding_model, **kwargs
        )
        if create.message != "Creation started":
            raise ValueError("Collection could not be created")

        if data is not None:
            insert = endpoints.insert_points_in_collection(
                self._client,
                name,
                self._data_to_httpx_file(data),
                normalize,
                resolve_chunking_dict(chunking_dict, chunking_method),
                parse_data,
                group=kwargs.get("group", None),
            )
            if insert.message != f"Documents inserted in {name}.":
                raise ValueError("Points could not be inserted into the collection")

        return self.details(name, kwargs.get("group", None))

    def insert_points(
        self,
        collection_name: str,
        data: Union[dict, CollectionDataset, str],
        normalize: bool = False,
        chunking_method: ChunkingMethod = "custom",
        chunking_dict: Optional[Dict[str, Any]] = None,
        parse_data: Optional[ParseDataInput] = None,
        **kwargs,
    ) -> CollectionDetails:
        insert = endpoints.insert_points_in_collection(
            self._client,
            collection_name,
            self._data_to_httpx_file(data),
            normalize,
            resolve_chunking_dict(chunking_dict, chunking_method),
            parse_data,
            group=kwargs.get("group", None),
        )
        if insert.message != f"Documents inserted in {collection_name}.":
            raise ValueError(
                f"Points could not be inserted into the collection : {insert.model_dump_json()}"
            )
        return self.details(collection_name, kwargs.get("group", None))

    def delete_points(
        self,
        collection_name: str,
        points: List[str],
        **kwargs,
    ) -> CollectionDetails:
        delete = endpoints.delete_points_in_collection(
            self._client,
            points,
            collection_name,
            **kwargs,
        )
        if (
            f'{len(points)} points deleted from collection "{collection_name}"'
            not in delete.message
        ):
            raise ValueError(
                f"Points could not be deleted from the collection : {delete.model_dump_json()}"
            )

        return self.details(collection_name, kwargs.get("group", None))

    def clear(
        self,
        collection_name: str,
        **kwargs,
    ) -> CollectionDetails:
        clear = endpoints.delete_all_points_in_collection(
            self._client,
            collection_name,
            **kwargs,
        )
        if (
            f'All points deleted from collection "{collection_name}" for group'
            not in clear.message
        ):
            raise ValueError(
                f"Points could not be deleted from the collection : {clear.model_dump_json()}"
            )
        return self.details(collection_name, kwargs.get("group", None))


class AsyncCollectionsModule(AsyncModule, AbstractCollectionsModule):
    def __init__(self, parent, client):
        AsyncModule.__init__(self, parent, client)
        AbstractCollectionsModule.__init__(self, parent, client)

    async def list(self) -> List[GroupCollections]:
        return await async_endpoints.collections(self._client)

    async def get_by_group(self, group_id: str) -> List[Collection]:
        collections = await self.list()
        return self._get_collections_by_group(collections, group_id)

    async def details(
        self, collection_id: str, group_id: Optional[str] = None
    ) -> CollectionDetails:
        points = await async_endpoints.collection(self._client, collection_id, group_id)

        return CollectionDetails(
            name=collection_id,
            group=group_id,
            points=points if points else [],
        )

    async def delete(self, name: str, **kwargs) -> bool:
        response = await async_endpoints.delete_collection(self._client, name, **kwargs)
        if response is None:
            raise ValueError("Collection could not be deleted")
        return True

    async def create(
        self,
        name: str,
        data: Optional[Union[dict, CollectionDataset, str]] = None,
        embedding_model: Optional[str] = "BAAI/bge-m3",
        normalize: bool = False,
        chunking_method: ChunkingMethod = "custom",
        chunking_dict: Optional[Dict[str, Any]] = None,
        parse_data: Optional[ParseDataInput] = None,
        **kwargs,
    ) -> CollectionDetails:
        create = await async_endpoints.create_collection(
            self._client, name, embedding_model, **kwargs
        )
        if create.message != "Creation started":
            raise ValueError("Collection could not be created")

        if data is not None:
            insert = await async_endpoints.insert_points_in_collection(
                self._client,
                name,
                self._data_to_httpx_file(data),
                normalize,
                resolve_chunking_dict(chunking_dict, chunking_method),
                parse_data,
                group=kwargs.get("group", None),
            )
            if insert.message != f"Documents inserted in {name}.":
                raise ValueError("Points could not be inserted into the collection")

        return await self.details(name, kwargs.get("group", None))

    async def insert_points(
        self,
        collection_name: str,
        data: Union[dict, CollectionDataset, str],
        normalize: bool = False,
        chunking_method: ChunkingMethod = "custom",
        chunking_dict: Optional[Dict[str, Any]] = None,
        parse_data: Optional[ParseDataInput] = None,
        **kwargs,
    ) -> CollectionDetails:
        insert = await async_endpoints.insert_points_in_collection(
            self._client,
            collection_name,
            self._data_to_httpx_file(data),
            normalize,
            resolve_chunking_dict(chunking_dict, chunking_method),
            parse_data,
            group=kwargs.get("group", None),
        )
        if insert.message != f"Documents inserted in {collection_name}.":
            raise ValueError(
                f"Points could not be inserted into the collection : {insert.model_dump_json()}"
            )

        return await self.details(collection_name, kwargs.get("group", None))

    async def delete_points(
        self,
        collection_name: str,
        points: List[str],
        **kwargs,
    ) -> CollectionDetails:
        delete = await async_endpoints.delete_points_in_collection(
            self._client,
            points,
            collection_name,
            **kwargs,
        )
        if (
            f'{len(points)} points deleted from collection "{collection_name}"'
            not in delete.message
        ):
            raise ValueError(
                f"Points could not be deleted from the collection : {delete.model_dump_json()}"
            )

        return await self.details(collection_name, kwargs.get("group", None))

    async def clear(
        self,
        collection_name: str,
        **kwargs,
    ) -> CollectionDetails:
        clear = await async_endpoints.delete_all_points_in_collection(
            self._client,
            collection_name,
            **kwargs,
        )
        if (
            f'All points deleted from collection "{collection_name}" for group'
            not in clear.message
        ):
            raise ValueError(
                f"Points could not be deleted from the collection : {clear.model_dump_json()}"
            )
        return await self.details(collection_name, kwargs.get("group", None))
