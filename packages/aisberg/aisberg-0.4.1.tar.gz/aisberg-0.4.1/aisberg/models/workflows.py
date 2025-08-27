from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict


class Workflow(BaseModel):
    name: str
    id: str
    group: str
    createdAt: datetime
    updatedAt: datetime
    description: Optional[str] = None
    isActive: Optional[bool] = True


class Input(BaseModel):
    input_id: str
    input_type: str
    input_name: str
    value: Dict[str, Any]
    linkable: bool


class WorkflowRunInput(BaseModel):
    input_name: str
    input_type: str


class Output(BaseModel):
    output_id: str
    output_type: str
    output_name: str
    linkable: bool


class Position(BaseModel):
    x: float
    y: float
    _id: str


class Node(BaseModel):
    inputs: List[Input]
    outputs: List[Output]
    node_id: str
    name: str
    source_nodes_id: Optional[List[str]]
    type: str
    target_nodes: List[Dict[str, Any]]
    position: Position
    _id: str


class WorkflowDetails(BaseModel):
    id: str
    group: str
    name: str
    createdAt: datetime
    updatedAt: datetime
    starting_node_id: str
    nodes: List[Node]


class WorkflowRunChunk(BaseModel):
    response: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class WorkflowRunResult(BaseModel):
    response: Optional[str] = None
    model_config = ConfigDict(extra="allow")
