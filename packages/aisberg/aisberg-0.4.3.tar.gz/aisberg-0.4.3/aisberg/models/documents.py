from io import BytesIO
from typing import Optional, List, Tuple, Union

from pydantic import BaseModel


class DocumentParserDocOutput(BaseModel):
    type: str
    data: Union[str, dict, list]


class DocumentParserResponse(BaseModel):
    """
    Response model for document parsing.
    """

    message: Optional[str] = None
    parsedFiles: Optional[List[DocumentParserDocOutput]] = None


class FileObject(BaseModel):
    """
    Represents a file object with its name and content.
    """

    name: str
    buffer: bytes


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
