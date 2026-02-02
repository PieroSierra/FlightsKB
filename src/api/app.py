"""FastAPI application for Flights KB."""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src import __version__


def create_app(
    index_dir: Optional[Path] = None,
    knowledge_dir: Optional[Path] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        index_dir: Path to index directory.
        knowledge_dir: Path to knowledge directory.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Flights KB API",
        description="A lightweight HTTP API for querying and managing the Flights KB knowledge base.",
        version=__version__,
    )

    # Add CORS middleware for console access
    cors_origins = os.environ.get(
        "FLIGHTSKB_CORS_ORIGINS",
        "http://localhost:5173,http://localhost:4173,https://pierosierra.github.io"
    ).split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store config in app state
    app.state.index_dir = index_dir or Path(os.environ.get("FLIGHTSKB_INDEX_DIR", "index"))
    app.state.knowledge_dir = knowledge_dir or Path(os.environ.get("FLIGHTSKB_KNOWLEDGE_DIR", "knowledge"))
    app.state.api_key = os.environ.get("FLIGHTSKB_API_KEY", "")

    # Include routes under /api prefix
    from src.api.routes import router
    app.include_router(router, prefix="/api")

    # Static file serving for console (production deployment)
    # Determine console dist path relative to this file or from env
    console_dist = Path(os.environ.get(
        "FLIGHTSKB_CONSOLE_DIR",
        Path(__file__).parent.parent.parent / "console" / "dist"
    ))

    if console_dist.exists():
        # Mount static assets (JS, CSS, etc.)
        assets_dir = console_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="console_assets")

        # SPA catch-all route - must be after API routes
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve React SPA for all non-API routes."""
            # Check for specific static files (favicon, etc.)
            if full_path:
                file_path = console_dist / full_path
                if file_path.is_file():
                    return FileResponse(file_path)

            # Return index.html for all routes (React Router handles routing)
            index_file = console_dist / "index.html"
            if index_file.exists():
                return FileResponse(index_file)

            return {"error": "Console not built", "hint": "Run: cd console && npm run build"}

        # Also handle root path
        @app.get("/")
        async def serve_spa_root():
            """Serve React SPA at root."""
            index_file = console_dist / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            return {"error": "Console not built", "hint": "Run: cd console && npm run build"}

    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
