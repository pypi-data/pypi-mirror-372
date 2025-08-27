from typing import Optional, List, Any

from pydantic import BaseModel


class ModelPermission(BaseModel):
    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    allow_create_engine: Optional[bool] = None
    allow_sampling: Optional[bool] = None
    allow_logprobs: Optional[bool] = None
    allow_search_indices: Optional[bool] = None
    allow_view: Optional[bool] = None
    allow_fine_tuning: Optional[bool] = None
    organization: Optional[str] = None
    group: Optional[Any] = None
    is_blocking: Optional[bool] = None


class ModelMeta(BaseModel):
    vocab_type: Optional[int] = None
    n_vocab: Optional[int] = None
    n_ctx_train: Optional[int] = None
    n_embd: Optional[int] = None
    n_params: Optional[int] = None
    size: Optional[int] = None


class Model(BaseModel):
    id: Optional[str] = None
    created: Optional[int] = None
    object: Optional[str] = None
    owned_by: Optional[str] = None
    root: Optional[str] = None
    parent: Optional[Any] = None
    max_model_len: Optional[int] = None
    permission: Optional[List[ModelPermission]] = None
    language: Optional[List[str]] = None
    meta: Optional[ModelMeta] = None
