"""API routes for Flights KB."""

import base64
from pathlib import Path
from typing import Optional, Literal

import frontmatter
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from pydantic import BaseModel, Field

from src.services.index import IndexService
from src.services.ingest import IngestService
from src.services.github import get_github_client, GitHubConfigurationError

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


class RebuildRequest(BaseModel):
    """Request body for rebuild endpoint."""

    source: Literal["local", "github"] = "github"
    force: bool = False


class RebuildResponse(BaseModel):
    """Response from rebuild endpoint."""

    success: bool
    documents_processed: int
    chunks_indexed: int
    duration_seconds: float
    errors: list[str] = []
    source: str = "local"


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


class GitHubCommitResult(BaseModel):
    """Result of a GitHub commit operation."""

    commit_sha: str
    commit_url: str
    file_path: str
    file_sha: str


class IngestResponse(BaseModel):
    """Response from ingest endpoint."""

    success: bool
    kb_id: str
    file_path: str
    title: str
    chunk_count: int
    github_commit: Optional[GitHubCommitResult] = None
    github_error: Optional[str] = None


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


class GitHubStatusResponse(BaseModel):
    """Response from GitHub status endpoint."""

    configured: bool
    owner: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    knowledge_file_count: Optional[int] = None


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
        error_msg = str(e)
        # Provide helpful message for empty/missing index
        if "no such table" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "INDEX_NOT_READY",
                    "message": "Vector index has not been built. Use POST /api/rebuild to initialize.",
                    "rebuild_url": "/api/rebuild",
                },
            )
        raise HTTPException(
            status_code=503,
            detail={"error": "INDEX_UNAVAILABLE", "message": error_msg},
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
    body: Optional[RebuildRequest] = None,
    index_service: IndexService = Depends(get_index_service),
    _: None = Depends(verify_api_key),
):
    """Rebuild the vector index. Requires API key.

    Can rebuild from local filesystem or from GitHub repository.
    """
    # Default to github source if GITHUB_TOKEN is configured
    source = "local"
    if body and body.source:
        source = body.source
    elif get_github_client() is not None:
        source = "github"

    try:
        if source == "github":
            # Rebuild from GitHub
            result = await _rebuild_from_github(index_service)
        else:
            # Rebuild from local filesystem
            result = index_service.rebuild(verbose=False)

        return RebuildResponse(
            success=result.get("success", True),
            documents_processed=result.get("documents_processed", 0),
            chunks_indexed=result.get("chunks_indexed", 0),
            duration_seconds=result.get("duration_seconds", 0),
            errors=result.get("errors", []),
            source=source,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "REBUILD_FAILED", "message": str(e)},
        )


async def _rebuild_from_github(index_service: IndexService) -> dict:
    """Fetch markdown files from GitHub and rebuild the index.

    After rebuilding, syncs any inbox file moves back to GitHub by:
    1. Deleting files from knowledge/inbox/ that were moved
    2. Creating files at their new destination categories
    """
    from datetime import datetime
    import tempfile
    import shutil

    start_time = datetime.now()
    errors = []

    github_client = get_github_client()
    if github_client is None:
        raise GitHubConfigurationError("GitHub integration not configured")

    # Fetch list of all markdown files from GitHub
    try:
        md_files = await github_client.list_markdown_files_recursive("knowledge")
    except Exception as e:
        raise Exception(f"Failed to list GitHub files: {e}")

    if not md_files:
        return {
            "success": True,
            "documents_processed": 0,
            "chunks_indexed": 0,
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "errors": ["No markdown files found in knowledge/ directory"],
        }

    # Create a temporary directory to store files
    temp_dir = Path(tempfile.mkdtemp(prefix="flightskb_github_"))

    # Track file SHAs for inbox files (needed for deletion)
    inbox_file_shas = {}

    try:
        # Download each file
        for file_path in md_files:
            try:
                github_file = await github_client.read_file(file_path)

                # Create local directory structure
                local_path = temp_dir / file_path
                local_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file content
                local_path.write_text(github_file.content)

                # Track SHA for inbox files
                if file_path.startswith("knowledge/inbox/"):
                    inbox_file_shas[Path(file_path).name] = github_file.sha
            except Exception as e:
                errors.append(f"Failed to fetch {file_path}: {e}")

        # Sync downloaded files to local knowledge directory so file browser stays in sync
        local_knowledge_dir = Path(index_service.knowledge_dir)
        try:
            if local_knowledge_dir.exists():
                shutil.rmtree(local_knowledge_dir)
            shutil.copytree(temp_dir / "knowledge", local_knowledge_dir)
        except Exception as e:
            errors.append(f"Warning: Failed to sync to local knowledge directory: {e}")

        # Create a temporary IndexService pointing to the temp directory
        from src.services.index import IndexService as TempIndexService

        temp_index_service = TempIndexService(
            index_dir=index_service.index_dir,
            knowledge_dir=temp_dir / "knowledge",
        )

        # Rebuild from the temporary directory, tracking file moves
        result = temp_index_service.rebuild(verbose=False, track_moves=True)
        result["errors"] = errors + result.get("errors", [])

        # Sync file moves back to GitHub
        file_moves = result.pop("file_moves", [])
        github_sync_results = await _sync_inbox_moves_to_github(
            github_client,
            file_moves,
            inbox_file_shas,
        )
        result["errors"].extend(github_sync_results["errors"])
        result["github_files_moved"] = github_sync_results["files_moved"]

    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

    result["duration_seconds"] = (datetime.now() - start_time).total_seconds()
    return result


async def _sync_inbox_moves_to_github(
    github_client,
    file_moves: list,
    inbox_file_shas: dict,
) -> dict:
    """Sync inbox file moves to GitHub.

    For each moved file:
    1. Create the file at the new destination
    2. Delete the original from inbox

    Args:
        github_client: GitHubContentsClient instance
        file_moves: List of FileMove objects from rebuild
        inbox_file_shas: Dict mapping filename to SHA for inbox files

    Returns:
        Dict with 'files_moved' count and 'errors' list
    """
    errors = []
    files_moved = 0

    for move in file_moves:
        filename = move.original_filename
        destination = move.destination_category
        new_content = move.new_content

        old_path = f"knowledge/inbox/{filename}"
        new_path = f"knowledge/{destination}/{filename}"
        sha = inbox_file_shas.get(filename)

        if not sha:
            errors.append(f"Cannot sync {filename}: SHA not found for deletion")
            continue

        try:
            # First, create the file at the new destination
            try:
                await github_client.create_file(
                    path=new_path,
                    content=new_content,
                    message=f"Move {filename} from inbox to {destination}",
                )
            except Exception as e:
                # File might already exist (409), try update instead
                if "422" in str(e) or "409" in str(e):
                    # Get the existing file's SHA
                    existing = await github_client.read_file(new_path)
                    await github_client.update_file(
                        path=new_path,
                        content=new_content,
                        message=f"Update {filename} in {destination} (moved from inbox)",
                        sha=existing.sha,
                    )
                else:
                    raise

            # Then, delete the original from inbox
            await github_client.delete_file(
                path=old_path,
                message=f"Remove {filename} from inbox (moved to {destination})",
                sha=sha,
            )

            files_moved += 1

        except Exception as e:
            errors.append(f"Failed to sync {filename} to GitHub: {e}")

    return {
        "files_moved": files_moved,
        "errors": errors,
    }


@router.post("/ingest", response_model=IngestResponse)
async def ingest_content(
    body: IngestRequest,
    request: Request,
    _: None = Depends(verify_api_key),
):
    """Ingest new content into the knowledge base. Requires API key.

    Content is saved locally and committed to GitHub for persistence.
    """
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

        # Commit to GitHub if configured
        github_commit = None
        github_error = None
        github_client = get_github_client()

        if github_client is not None:
            try:
                # Read the file that was just created
                local_file = Path(result["file_path"])
                file_content = local_file.read_text()

                # Determine the GitHub path (relative to repo root)
                # File is in knowledge/inbox/{kb_id}.md
                github_path = f"knowledge/inbox/{local_file.name}"

                # Commit to GitHub
                commit_result = await github_client.create_file(
                    path=github_path,
                    content=file_content,
                    message=f"Add {result['title']} via FlightsKB console",
                )

                github_commit = GitHubCommitResult(
                    commit_sha=commit_result.commit_sha,
                    commit_url=commit_result.commit_url,
                    file_path=commit_result.file_path,
                    file_sha=commit_result.file_sha,
                )
            except Exception as e:
                github_error = str(e)

        return IngestResponse(
            success=True,
            kb_id=result["kb_id"],
            file_path=result["file_path"],
            title=result["title"],
            chunk_count=result.get("chunk_count", 1),
            github_commit=github_commit,
            github_error=github_error,
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


@router.get("/github/status", response_model=GitHubStatusResponse)
async def get_github_status(
    _: None = Depends(verify_api_key),
):
    """Check GitHub integration status. Requires API key."""
    client = get_github_client()

    if client is None:
        return GitHubStatusResponse(configured=False)

    try:
        # Get rate limit to verify token works
        rate_limit = await client.get_rate_limit()

        # Count knowledge files
        try:
            md_files = await client.list_markdown_files_recursive("knowledge")
            file_count = len(md_files)
        except Exception:
            file_count = None

        return GitHubStatusResponse(
            configured=True,
            owner=client.config.owner,
            repo=client.config.repo,
            branch=client.config.branch,
            rate_limit_remaining=rate_limit.get("remaining"),
            knowledge_file_count=file_count,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "GITHUB_ERROR",
                "message": f"GitHub API error: {str(e)}",
            },
        )
