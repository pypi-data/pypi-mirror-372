from typing import List, Optional, Dict, Any, Literal, Union

from pydantic import BaseModel, RootModel, ConfigDict


class EmbeddingItem(BaseModel):
    embedding: List[float]
    index: int
    object: str


class UsageDetails(BaseModel):
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int
    prompt_tokens_details: Optional[dict] = None


class EncodingResponse(BaseModel):
    id: str
    object: str
    model: str
    created: int
    data: List[EmbeddingItem]
    usage: UsageDetails


class ChunkData(BaseModel):
    id: str
    idx: int
    filename: str
    text: str
    collection_name: str
    filetype: str
    dense_encoder: str
    sparse_encoder: str
    timestamp: str
    norm: Optional[Union[bool, str]] = None
    rrf_score: Optional[float] = None
    chunk_method: Optional[str] = None

    # Pour permettre l'ajout de clés dynamiques pour les métadonnées
    model_config = ConfigDict(extra="allow")

    def metadata(self) -> Dict[str, Any]:
        """Retourne les métadonnées du ChunkData."""
        fields = set(self.model_fields.keys())
        return {k: v for k, v in self.model_dump().items() if k not in fields}


class ChunksDataList(RootModel[List[ChunkData]]):
    def metadata(self) -> List[Dict[str, Any]]:
        """Retourne une liste des métadonnées de chaque ChunkData."""
        return [chunk.metadata() for chunk in self.root]

    def texts(self) -> List[str]:
        """Retourne une liste des textes de chaque ChunkData."""
        return [chunk.text for chunk in self.root]

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, idx):
        return self.root[idx]

    def append(self, value: ChunkData):
        self.root.append(value)

    def extend(self, values: List[ChunkData]):
        self.root.extend(values)

    def to_list(self) -> List[ChunkData]:
        return list(self.root)

    def to_dict(self) -> List[dict]:
        return [c.model_dump() for c in self.root]

    def __repr__(self):
        return f"ChunksDataList({self.root!r})"

    def filter_by_collection(self, name: str) -> "ChunksDataList":
        return ChunksDataList.model_validate(
            [c for c in self.root if c.collection_name == name]
        )


class RerankerDocument(BaseModel):
    text: str


class RerankerResult(BaseModel):
    index: int
    document: RerankerDocument
    relevance_score: float


class RerankerResponse(BaseModel):
    id: str
    model: str
    usage: Dict[str, int]
    results: List[RerankerResult]

    def filter_by_relevance_score(self, threshold: float) -> "RerankerResponse":
        """Retourne une nouvelle instance filtrée de RerankerResponse."""
        filtered_results = [
            result for result in self.results if result.relevance_score >= threshold
        ]
        return RerankerResponse(
            id=self.id, model=self.model, usage=self.usage, results=filtered_results
        )


EncodingFormat = Optional[Literal["float", "base64"]]
