"""FastAPI application for Flights KB."""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    # Include routes
    from src.api.routes import router
    app.include_router(router)

    return app
