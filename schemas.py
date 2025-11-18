"""
Database Schemas for AI Hijabi Model Studio

Each Pydantic model corresponds to a MongoDB collection (lowercased name).
These are used for validation and are exposed via the /schema endpoint for tools.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class Model(BaseModel):
    """
    Represents a creator's reusable hijabi model identity
    Collection: "model"
    """
    name: str = Field(..., description="Model name (e.g., Aisha v1)")
    description: Optional[str] = Field(None, description="Notes about look and brand fit")
    identity_seed: Optional[str] = Field(None, description="Seed value for identity consistency")
    tags: List[str] = Field(default_factory=list, description="Keywords like modest, urban, pastel")
    style_preset: Optional[str] = Field(None, description="High-level preset (studio, street, editorial)")
    face_embeddings: Optional[List[str]] = Field(None, description="Embedding ids for face consistency")
    consistency_profile: Dict[str, Any] = Field(default_factory=dict, description="Parameters to enforce consistency")


class Pipeline(BaseModel):
    """
    Visual pipeline definition composed of nodes and edges
    Collection: "pipeline"
    """
    name: str
    version: str = "1.0"
    is_active: bool = True
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Pipeline nodes (loader, lora, control, render)")
    edges: List[Dict[str, Any]] = Field(default_factory=list, description="Connections between nodes")


class Dataset(BaseModel):
    """
    Group of generated/curated images to train fine-tunes (LoRA-like)
    Collection: "dataset"
    """
    model_id: Optional[str] = Field(None, description="Associated model identity")
    title: str = Field(..., description="Dataset title")
    status: Literal["idle", "building", "ready", "failed"] = "idle"
    size: int = 0
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Images and annotations")


class Job(BaseModel):
    """
    Generation or dataset job tracked by the system
    Collection: "job"
    """
    type: Literal[
        "face", "fullbody", "angles360", "expression", "background", "dress", "dataset"
    ]
    model_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["queued", "running", "succeeded", "failed"] = "queued"
    progress: int = 0
    output: List[Dict[str, Any]] = Field(default_factory=list, description="Generated assets or dataset references")


# Backwards-compatible sample schemas retained for reference (not used by the app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
