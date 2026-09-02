from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


# Health Check Models
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


# Repository Models
class CloneRepoRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to clone and index")
    repo_name: Optional[str] = Field(None, description="Optional custom repository folder name")


class RepoInfoResponse(BaseModel):
    repo_id: str
    repo_path: str
    manifest: Optional[Dict[str, Any]] = None


class RepoStructureResponse(BaseModel):
    repo_id: str
    structure: str


class RepoFileResponse(BaseModel):
    repo_id: str
    path: str
    content: str


class DeleteRepoResponse(BaseModel):
    repo_id: str
    message: str


# Search Models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query or concept")
    symbol_name: Optional[str] = Field(None, description="Target symbol name if applicable")
    keywords: Optional[List[str]] = Field(None, description="Keywords to match")
    limit: int = Field(10, ge=1, le=50, description="Max results to return")
    strategies: Optional[List[str]] = Field(
        default=["semantic", "symbol", "literal", "relationship"],
        description="Retrieval strategies to use"
    )


class SearchResponse(BaseModel):
    repo_id: str
    query: str
    total_results: int
    results: List[Dict[str, Any]]


# Symbol Models
class SymbolResponse(BaseModel):
    repo_id: str
    symbol_name: str
    total_matches: int
    symbols: List[Dict[str, Any]]


# Relationship Models
class RelationshipResponse(BaseModel):
    repo_id: str
    symbol_name: str
    direction: str
    outgoing: List[Dict[str, Any]] = []
    incoming: List[Dict[str, Any]] = []


# Ask Models
class AskRequest(BaseModel):
    question: str = Field(..., description="Question to ask the codebase mentor agent")


class AskResponse(BaseModel):
    repo_id: str
    question: str
    status: str
    answer: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None
    state: Dict[str, Any]
    evidence: List[Dict[str, Any]]
