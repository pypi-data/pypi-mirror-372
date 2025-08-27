import logging
import warnings
from abc import ABC, abstractmethod
from io import BytesIO
from typing import List

from ..abstract.modules import SyncModule, AsyncModule
from ..api import endpoints, async_endpoints
from ..models.documents import (
    FileObject,
    DocumentParserFileInput,
    ParsedDocument,
    DocumentParserDocOutput,
)
from ..models.requests import HttpxFileField

logger = logging.getLogger(__name__)


class AbstractDocumentsModule(ABC):
    def __init__(self, parent, client):
        self._parent = parent
        self._client = client

    @abstractmethod
    def parse(
        self, files: DocumentParserFileInput, **kwargs
    ) -> List[ParsedDocument]: ...

    @staticmethod
    def _prepare_files_payload(
        files: DocumentParserFileInput,
    ) -> HttpxFileField:
        """
        Prepares input files into a format compatible with HTTPX multipart uploads.

        Args:
            files (DocumentParserFileInput): Files to upload (see type for options).

        Returns:
            HttpxFileField: HTTPX-style list for multipart upload.

        Raises:
            TypeError: On unsupported type.
        """

        def to_file_tuple(item):
            # FileObject case
            if "FileObject" in globals() and isinstance(item, FileObject):
                content = item.buffer
                filename = item.name
            # (bytes, filename) tuple
            elif isinstance(item, tuple) and len(item) == 2:
                content, filename = item
            # bytes or BytesIO
            elif isinstance(item, (bytes, BytesIO)):
                content = item
                filename = "file"
            # str (filepath)
            elif isinstance(item, str):
                with open(item, "rb") as f:
                    content = f.read()
                filename = item.split("/")[-1]
            else:
                raise TypeError(
                    f"Unsupported file input type: {type(item)}. "
                    "Expected str, bytes, BytesIO, tuple, or FileObject."
                )
            # Normalize to BytesIO for HTTPX
            if isinstance(content, bytes):
                content = BytesIO(content)
            elif isinstance(content, BytesIO):
                content.seek(0)
            else:
                raise TypeError(
                    f"File content must be bytes or BytesIO, got {type(content)}"
                )
            return (filename, content)

        if isinstance(files, list):
            if len(files) == 0:
                raise ValueError("File list cannot be empty.")
            elif len(files) > 10:
                raise ValueError("Too many files provided. Maximum is 10.")

            normalized = [to_file_tuple(f) for f in files]
        else:
            normalized = [to_file_tuple(files)]

        # HTTPX format: [("files", (filename, fileobj, mimetype)), ...]
        httpx_files = [
            ("files", (filename, content, "application/octet-stream"))
            for filename, content in normalized
        ]
        return httpx_files

    @staticmethod
    def _normalize_response(
        files: HttpxFileField, parsed_files: List[DocumentParserDocOutput]
    ):
        """
        Normalize DocumentParserResponse to ParsedDocument

        :param parsed_files:
        :return:
        """
        if not parsed_files:
            raise ValueError("")

        if len(parsed_files) != len(files):
            warnings.warn(
                f"[Doc Parser] Be careful, one or more of your files haven't been parsed. Only {len(parsed_files)}/{len(files)} have been parsed."
            )

        parsed_documents = []

        for file, parsed_file in zip(files, parsed_files):
            parsed_documents.append(
                ParsedDocument(
                    content=parsed_file,
                    metadata={"name": file[1][0], "mimetype": file[1][2]},
                )
            )

        return parsed_documents


class SyncDocumentsModule(SyncModule, AbstractDocumentsModule):
    def __init__(self, parent, client):
        SyncModule.__init__(self, parent, client)
        AbstractDocumentsModule.__init__(self, parent, client)

    def parse(self, files, **kwargs) -> List[ParsedDocument]:
        httpx_files = self._prepare_files_payload(files)

        parsed_files = endpoints.parse_documents(
            self._client,
            httpx_files,
            **kwargs,
        )

        print(parsed_files)

        return self._normalize_response(httpx_files, parsed_files.parsedFiles)


class AsyncDocumentsModule(AsyncModule, AbstractDocumentsModule):
    def __init__(self, parent, client):
        AsyncModule.__init__(self, parent, client)
        AbstractDocumentsModule.__init__(self, parent, client)

    async def parse(self, files, **kwargs) -> List[ParsedDocument]:
        httpx_files = self._prepare_files_payload(files)

        parsed_files = await async_endpoints.parse_documents(
            self._client,
            httpx_files,
            **kwargs,
        )

        return self._normalize_response(httpx_files, parsed_files.parsedFiles)
