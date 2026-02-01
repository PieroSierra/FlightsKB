"""API routes for Flights KB."""

import base64
from pathlib import Path
from typing import Optional, Literal

import frontmatter
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from pydantic import BaseModel, Field

from src.services.index import IndexService
from src.services.ingest import IngestService

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


class IngestRequest(BaseModel):
    """Request body for ingest endpoint."""

    content_type: Literal["text", "txt", "pdf", "html"]
    content: str = Field(..., max_length=7340032)  # ~5MB base64
    filename: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(default="inbox", max_length=50)
    kind: Optional[str] = Field(default="internal", max_length=50)
    confidence: Optional[str] = Field(default="medium", max_length=20)


class IngestResponse(BaseModel):
    """Response from ingest endpoint."""

    success: bool
    kb_id: str
    file_path: str
    title: str
    chunk_count: int


class CategoriesResponse(BaseModel):
    """Response from categories endpoint."""

    categories: list[str]
    default: str = "inbox"


class FileTreeNode(BaseModel):
    """A node in the file tree."""

    name: str
    path: str
    type: Literal["file", "directory"]
    children: Optional[list["FileTreeNode"]] = None
    metadata: Optional[dict] = None


class FileTreeResponse(BaseModel):
    """Response from file tree endpoint."""

    root: str
    tree: list[FileTreeNode]


class FileContentResponse(BaseModel):
    """Response from file content endpoint."""

    path: str
    filename: str
    content: str
    frontmatter: dict


# Size limits
MAX_TEXT_SIZE = 100 * 1024  # 100KB for plain text
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB for files


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


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(request: Request):
    """Get available knowledge categories (subdirectories).

    Returns destination categories for ingestion (excludes inbox which is staging area).
    """
    knowledge_dir = Path(request.app.state.knowledge_dir)
    categories = sorted([
        d.name for d in knowledge_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "inbox"
    ])
    # Default to first category if available, otherwise empty string
    default = categories[0] if categories else ""
    return CategoriesResponse(categories=categories, default=default)


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


@router.post("/ingest", response_model=IngestResponse)
async def ingest_content(
    body: IngestRequest,
    request: Request,
    _: None = Depends(verify_api_key),
):
    """Ingest new content into the knowledge base. Requires API key."""
    try:
        # Decode content based on type
        if body.content_type == "text":
            # Plain text - check size
            if len(body.content.encode("utf-8")) > MAX_TEXT_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail={
                        "error": "CONTENT_TOO_LARGE",
                        "message": f"Text content exceeds {MAX_TEXT_SIZE // 1024}KB limit",
                    },
                )
            content = body.content
            content_bytes = None
        else:
            # Base64 encoded file
            try:
                content_bytes = base64.b64decode(body.content)
                if len(content_bytes) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail={
                            "error": "CONTENT_TOO_LARGE",
                            "message": f"File content exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB limit",
                        },
                    )
                content = None
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "INVALID_CONTENT",
                        "message": "Invalid base64 encoding for file content",
                    },
                )

        # Initialize ingest service
        ingest_service = IngestService(
            knowledge_dir=request.app.state.knowledge_dir,
        )

        # Prepare metadata for ingestion
        ingest_kwargs = {
            "source_kind": body.kind or "internal",
            "title": body.title,
            "category": body.category or "inbox",
            "confidence": body.confidence or "medium",
        }

        # Perform ingestion based on content type
        if body.content_type == "text":
            result = ingest_service.ingest_text(content, **ingest_kwargs)
        elif body.content_type == "txt":
            result = ingest_service.ingest_txt(content_bytes, **ingest_kwargs)
        elif body.content_type == "pdf":
            result = ingest_service.ingest_pdf(content_bytes, **ingest_kwargs)
        elif body.content_type == "html":
            result = ingest_service.ingest_html(content_bytes, **ingest_kwargs)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_CONTENT",
                    "message": f"Unsupported content type: {body.content_type}",
                },
            )

        return IngestResponse(
            success=True,
            kb_id=result["kb_id"],
            file_path=result["file_path"],
            title=result["title"],
            chunk_count=result.get("chunk_count", 1),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "PARSE_FAILED", "message": str(e)},
        )


def _is_safe_path(base_path: Path, requested_path: str) -> Path:
    """Validate path to prevent directory traversal attacks.

    Returns the resolved absolute path if safe, raises HTTPException otherwise.
    """
    # Normalize and resolve the full path
    full_path = (base_path / requested_path).resolve()

    # Ensure the resolved path is still under base_path
    try:
        full_path.relative_to(base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_PATH", "message": "Path traversal not allowed"},
        )

    return full_path


def _build_file_tree(directory: Path, base_path: Path) -> list[FileTreeNode]:
    """Recursively build the file tree for a directory."""
    nodes = []

    try:
        entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return nodes

    for entry in entries:
        if entry.name.startswith("."):
            continue

        relative_path = str(entry.relative_to(base_path))

        if entry.is_dir():
            children = _build_file_tree(entry, base_path)
            nodes.append(FileTreeNode(
                name=entry.name,
                path=relative_path,
                type="directory",
                children=children,
            ))
        elif entry.suffix == ".md":
            # Extract frontmatter metadata for markdown files
            metadata = {}
            try:
                post = frontmatter.load(str(entry))
                metadata = {
                    "kb_id": post.get("kb_id", ""),
                    "title": post.get("title", entry.stem),
                    "status": post.get("status", ""),
                }
            except Exception:
                metadata = {"title": entry.stem}

            nodes.append(FileTreeNode(
                name=entry.name,
                path=relative_path,
                type="file",
                metadata=metadata,
            ))

    return nodes


@router.get("/files/tree", response_model=FileTreeResponse)
async def get_file_tree(request: Request):
    """Get the hierarchical file tree of the knowledge directory."""
    knowledge_dir = Path(request.app.state.knowledge_dir)

    if not knowledge_dir.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Knowledge directory not found"},
        )

    tree = _build_file_tree(knowledge_dir, knowledge_dir)

    return FileTreeResponse(
        root="knowledge",
        tree=tree,
    )


@router.get("/files/content", response_model=FileContentResponse)
async def get_file_content(
    request: Request,
    path: str = Query(..., description="Relative path to the file"),
):
    """Get the content and frontmatter of a markdown file."""
    knowledge_dir = Path(request.app.state.knowledge_dir)

    # Validate path to prevent directory traversal
    full_path = _is_safe_path(knowledge_dir, path)

    if not full_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"File not found: {path}"},
        )

    if not full_path.is_file():
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_PATH", "message": "Path is not a file"},
        )

    if full_path.suffix != ".md":
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_FILE", "message": "Only markdown files are supported"},
        )

    try:
        post = frontmatter.load(str(full_path))
        content = post.content
        fm = dict(post.metadata)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "PARSE_FAILED", "message": f"Failed to parse file: {e}"},
        )

    return FileContentResponse(
        path=path,
        filename=full_path.name,
        content=content,
        frontmatter=fm,
    )
