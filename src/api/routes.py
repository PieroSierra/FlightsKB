"""API routes for Flights KB."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field

from src.services.index import IndexService

router = APIRouter()


# Request/Response models
class QueryRequest(BaseModel):
    """Request body for query endpoint."""

    text: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=50)
    filters: Optional[dict] = None


class ChunkResult(BaseModel):
    """A single search result."""

    chunk_id: str
    kb_id: str
    title: str
    text: str
    score: float
    metadata: dict = {}
    file_path: Optional[str] = None


class QueryResponse(BaseModel):
    """Response from query endpoint."""

    query: str
    total_results: int
    results: list[ChunkResult]


class StatsResponse(BaseModel):
    """Response from stats endpoint."""

    document_count: int
    chunk_count: int
    by_type: dict = {}
    by_category: dict = {}
    by_confidence: dict = {}
    by_status: dict = {}
    index_metadata: dict = {}


class RebuildResponse(BaseModel):
    """Response from rebuild endpoint."""

    success: bool
    documents_processed: int
    chunks_indexed: int
    duration_seconds: float
    errors: list[str] = []


class HealthResponse(BaseModel):
    """Response from health endpoint."""

    status: str
    version: str


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    message: str
    details: Optional[dict] = None


def get_index_service(request: Request) -> IndexService:
    """Dependency to get index service."""
    return IndexService(
        index_dir=request.app.state.index_dir,
        knowledge_dir=request.app.state.knowledge_dir,
    )


def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None),
):
    """Verify API key for protected endpoints."""
    expected_key = request.app.state.api_key
    if not expected_key:
        # No key configured, allow access
        return
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail={"error": "UNAUTHORIZED", "message": "Invalid or missing API key"},
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from src import __version__
    return HealthResponse(status="healthy", version=__version__)


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    body: QueryRequest,
    index_service: IndexService = Depends(get_index_service),
):
    """Search the knowledge base."""
    try:
        response = index_service.query(
            text=body.text,
            k=body.k,
            filters=body.filters,
        )

        return QueryResponse(
            query=response.query,
            total_results=response.total_results,
            results=[
                ChunkResult(
                    chunk_id=r.chunk_id,
                    kb_id=r.kb_id,
                    title=r.title,
                    text=r.text,
                    score=r.score,
                    metadata=r.metadata,
                    file_path=r.file_path,
                )
                for r in response.results
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"error": "INDEX_UNAVAILABLE", "message": str(e)},
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    index_service: IndexService = Depends(get_index_service),
):
    """Get knowledge base statistics."""
    try:
        stats = index_service.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"error": "INDEX_UNAVAILABLE", "message": str(e)},
        )


@router.post("/rebuild", response_model=RebuildResponse)
async def rebuild_index(
    index_service: IndexService = Depends(get_index_service),
    _: None = Depends(verify_api_key),
):
    """Rebuild the vector index. Requires API key."""
    try:
        result = index_service.rebuild(verbose=False)
        return RebuildResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "REBUILD_FAILED", "message": str(e)},
        )
