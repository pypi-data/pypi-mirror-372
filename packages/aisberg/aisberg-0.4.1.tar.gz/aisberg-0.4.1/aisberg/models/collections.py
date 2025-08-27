from typing import List, Optional, Union, Literal, Dict, Any

from pydantic import BaseModel


class Collection(BaseModel):
    name: str


class GroupCollections(BaseModel):
    group: str
    collections: List[Collection]


class CollectionDataset(BaseModel):
    chunks: List[str]
    metadata: Optional[dict] = []


class CollectionCreateResponse(BaseModel):
    message: Optional[str] = None


ChunkingMethod = Literal["semantic", "custom", "delimiter"]

_DEFAULTS_CHUNKING_METHODS: Dict[ChunkingMethod, Dict[str, Any]] = {
    "delimiter": {
        "method": "delimiter",
        "params": {"delimiters": ".", "max_chunk_size": 30, "chunk_overlap": 5},
    },
    "custom": {
        "method": "custom",
        "params": {},
    },
    "semantic": {
        "method": "semantic",
        "params": {
            "encoder": "BAAI/bge-m3",
            "threshold_strategy": "percentile",
            "breakpoint_threshold": 95,
            "buffer_size": 2,
            "use_split_cs": False,
        },
    },
}


def resolve_chunking_dict(
    chunking_dict: Optional[Dict[str, Any]],
    chunking_method: ChunkingMethod = "semantic",
) -> Dict[str, Any]:
    if chunking_method not in _DEFAULTS_CHUNKING_METHODS:
        raise ValueError(f"chunking_method invalide: {chunking_method}")

    if chunking_dict is None:
        base = _DEFAULTS_CHUNKING_METHODS[chunking_method]
        return {"method": base["method"], "params": dict(base["params"])}

    method = chunking_dict.get("method", chunking_method)
    params = dict(chunking_dict.get("params", {}))
    return {"method": method, "params": params}


class ParseDataInput(BaseModel):
    source: Optional[str] = None
    diarize: Optional[bool] = False
    input: Optional[str] = None
    group: Optional[str] = None
    stt_model: Optional[str] = None
    vlm_model: Optional[str] = None


# Modèle plus structuré pour payload
class Payload(BaseModel):
    method: Optional[str] = None
    norm: Optional[Union[str, bool]] = None
    filetype: Optional[str] = None
    filename: Optional[str] = None
    dense_encoder: Optional[str] = None
    Category: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[str] = None
    collection_name: Optional[str] = None
    sparse_encoder: Optional[str] = None


class PointDetails(BaseModel):
    id: str
    payload: Payload


class CollectionDetails(BaseModel):
    name: str
    group: Optional[str] = None
    points: List[PointDetails]
