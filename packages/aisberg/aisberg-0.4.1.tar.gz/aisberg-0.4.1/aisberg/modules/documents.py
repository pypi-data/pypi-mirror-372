import json
import logging
from abc import ABC, abstractmethod
from io import BytesIO
from typing import List

from ..abstract.modules import SyncModule, AsyncModule
from ..api import endpoints, async_endpoints
from ..models.documents import (
    FileObject,
    DocumentParserFileInput,
    ParsedDocument,
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

    def _get_parsed_files_from_s3(
        self, files: List[str], bucket_name: str
    ) -> List[ParsedDocument]:
        """
        Download and parse a list of files from an S3 bucket.

        Args:
            files (List[str]): List of file names to download from S3.
            bucket_name (str): Name of the S3 bucket.

        Returns:
            List[ParsedDocument]: Parsed documents as objects with content and metadata.

        Raises:
            Exception: If a file cannot be downloaded or parsed.
        """
        parsed_documents = []
        for file_name in files:
            if not file_name.endswith(".json"):
                if '"type": "error"' in file_name:
                    logger.error(f"[DOCUMENT PARSER] Parsing failed => {file_name}. ")
                continue

            logger.debug(f"Downloading file {file_name} from bucket {bucket_name}")
            # Download the file as a BytesIO
            doc_bytesio = self._parent._s3.download_file(bucket_name, file_name)
            try:
                buffer = doc_bytesio.getvalue()
                content_str = buffer.decode("utf-8")
                content_json = json.loads(content_str)
            finally:
                doc_bytesio.close()
            file_object = FileObject(name=file_name, buffer=buffer)
            parsed_documents.append(
                ParsedDocument(
                    content=content_json, metadata={"name": file_object.name}
                )
            )
        return parsed_documents

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


class SyncDocumentsModule(SyncModule, AbstractDocumentsModule):
    def __init__(self, parent, client):
        SyncModule.__init__(self, parent, client)
        AbstractDocumentsModule.__init__(self, parent, client)

    def parse(self, files, **kwargs) -> List[ParsedDocument]:
        output = endpoints.parse_documents(
            self._client,
            self._prepare_files_payload(files),
            **kwargs,
        )
        if output.message == "Files parsed successfully":
            return self._get_parsed_files_from_s3(output.parsedFiles, output.bucketName)
        else:
            raise ValueError(f"Error parsing files: {output.message}")


class AsyncDocumentsModule(AsyncModule, AbstractDocumentsModule):
    def __init__(self, parent, client):
        AsyncModule.__init__(self, parent, client)
        AbstractDocumentsModule.__init__(self, parent, client)

    async def parse(self, files, **kwargs) -> List[ParsedDocument]:
        output = await async_endpoints.parse_documents(
            self._client,
            self._prepare_files_payload(files),
            **kwargs,
        )
        if output.message == "Files parsed successfully":
            return self._get_parsed_files_from_s3(output.parsedFiles, output.bucketName)
        else:
            raise ValueError(f"Error parsing files: {output.message}")
