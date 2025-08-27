from io import BytesIO
from typing import Optional, List, Tuple, Union

from pydantic import BaseModel


class DocumentParserResponse(BaseModel):
    """
    Response model for document parsing.
    """

    message: Optional[str] = None
    parsedFiles: Optional[List[str]] = None
    bucketName: Optional[str] = None


class FileObject(BaseModel):
    """
    Represents a file object with its name and content.
    """

    name: str
    buffer: bytes


class DocumentParserDocOutput(BaseModel):
    type: str
    data: Union[str, dict, list]


class ParsedDocument(BaseModel):
    """
    Represents a parsed document with its content and metadata.
    """

    content: DocumentParserDocOutput
    metadata: Optional[dict] = None


DocumentParserFileInput = Union[
    str,
    bytes,
    BytesIO,
    Tuple[bytes, str],
    "FileObject",
    List[Union[str, bytes, BytesIO, Tuple[bytes, str], "FileObject"]],
]
