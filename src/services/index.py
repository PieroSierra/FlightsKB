"""Index service for ChromaDB operations."""

import json
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import chromadb
import frontmatter
from chromadb.config import Settings

from src.models.chunk import Chunk
from src.models.query import QueryResponse, QueryResult
from src.services.chunker import Chunker
from src.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class FileMove:
    """Represents a file move from inbox to destination category."""

    original_filename: str
    destination_category: str
    new_content: str

COLLECTION_NAME = "flights_kb"
METADATA_FILE = "rebuild_metadata.json"


class IndexService:
    """Service for managing the ChromaDB vector index."""

    def __init__(
        self,
        index_dir: Path,
        knowledge_dir: Path,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """
        Initialize the index service.

        Args:
            index_dir: Directory for ChromaDB persistence.
            knowledge_dir: Directory containing knowledge markdown files.
            embedding_service: Optional embedding service instance.
        """
        self.index_dir = Path(index_dir)
        self.knowledge_dir = Path(knowledge_dir)
        self.chroma_dir = self.index_dir / "chroma_db"
        self.metadata_file = self.index_dir / "manifests" / METADATA_FILE

        self._embedding_service = embedding_service
        self._client = None
        self._collection = None

    @property
    def embedding_service(self) -> EmbeddingService:
        """Lazy-load embedding service."""
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    @property
    def client(self) -> chromadb.ClientAPI:
        """Lazy-load ChromaDB client."""
        if self._client is None:
            self.chroma_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self.chroma_dir),
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def query(
        self,
        text: str,
        k: int = 5,
        filters: Optional[dict] = None,
    ) -> QueryResponse:
        """
        Query the knowledge base.

        Args:
            text: Natural language query text.
            k: Number of results to return.
            filters: Optional metadata filters.

        Returns:
            QueryResponse with ranked results.
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_single(text)

        # Build ChromaDB where clause
        where = self._build_where_clause(filters) if filters else None

        # Query the collection
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return QueryResponse(query=text, total_results=0, results=[])

        # Convert to QueryResponse
        query_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 0

                # Convert distance to similarity score (cosine distance to similarity)
                score = 1 - distance

                query_results.append(
                    QueryResult(
                        chunk_id=chunk_id,
                        kb_id=metadata.get("kb_id", ""),
                        title=metadata.get("title", ""),
                        text=document,
                        score=round(score, 4),
                        metadata=metadata,
                        file_path=metadata.get("file_path"),
                    )
                )

        return QueryResponse(
            query=text,
            total_results=len(query_results),
            results=query_results,
        )

    def _process_inbox_files(
        self,
        verbose: bool = False,
        track_moves: bool = False,
    ) -> tuple[list[str], list[FileMove]]:
        """
        Move files from inbox to their destination categories.

        Files with destination_category in frontmatter are moved to
        /knowledge/{destination_category}/ and the tag is removed.

        Args:
            verbose: Print progress information.
            track_moves: If True, track and return information about moved files.

        Returns:
            Tuple of (error messages, file moves if track_moves=True else empty list).
        """
        errors = []
        moves = []
        inbox_dir = self.knowledge_dir / "inbox"

        if not inbox_dir.exists():
            return errors, moves

        for file_path in inbox_dir.glob("*.md"):
            try:
                # Read file and parse frontmatter
                with open(file_path) as f:
                    post = frontmatter.load(f)

                destination = post.metadata.get("destination_category")
                if not destination:
                    continue  # No destination, leave in inbox

                # Validate destination directory exists or can be created
                dest_dir = self.knowledge_dir / destination
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Remove destination_category from metadata (file is now in the right place)
                del post.metadata["destination_category"]

                # Update status from draft to reviewed (optional enhancement)
                if post.metadata.get("status") == "draft":
                    post.metadata["status"] = "reviewed"
                post.metadata["updated"] = datetime.now().date().isoformat()

                # Generate the new content
                new_content = frontmatter.dumps(post)

                # Write to destination
                dest_file = dest_dir / file_path.name
                with open(dest_file, "w") as f:
                    f.write(new_content)

                # Remove original file from inbox
                file_path.unlink()

                if verbose:
                    logger.info(f"Moved {file_path.name} to {destination}/")

                # Track the move if requested
                if track_moves:
                    moves.append(FileMove(
                        original_filename=file_path.name,
                        destination_category=destination,
                        new_content=new_content,
                    ))

            except Exception as e:
                error_msg = f"Failed to process inbox file {file_path.name}: {e}"
                errors.append(error_msg)
                if verbose:
                    logger.error(error_msg)

        return errors, moves

    def rebuild(
        self,
        verbose: bool = False,
        track_moves: bool = False,
    ) -> dict:
        """
        Rebuild the index from knowledge directory.

        First moves files from inbox to their destination categories,
        then rebuilds the vector index.

        Args:
            verbose: Print progress information.
            track_moves: If True, include file move information in the result.

        Returns:
            Dictionary with rebuild statistics. If track_moves=True,
            includes 'file_moves' key with list of FileMove objects.
        """
        start_time = datetime.now()

        # Process inbox files first - move to destination categories
        inbox_errors, file_moves = self._process_inbox_files(
            verbose=verbose,
            track_moves=track_moves,
        )

        # Clear existing collection
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = None

        # Chunk all documents
        chunker = Chunker()
        chunks, errors = chunker.chunk_directory(self.knowledge_dir)
        errors = inbox_errors + errors

        if verbose and errors:
            for error in errors:
                logger.warning(f"Error: {error}")

        # Index chunks in batches
        if chunks:
            self._index_chunks(chunks, verbose=verbose)

        # Save metadata
        duration = (datetime.now() - start_time).total_seconds()
        metadata = {
            "last_rebuild": datetime.now().isoformat(),
            "embedding_model": self.embedding_service.model_name,
            "embedding_dimensions": self.embedding_service.dimensions,
            "document_count": len(set(c.doc_id for c in chunks)),
            "chunk_count": len(chunks),
            "duration_seconds": round(duration, 2),
            "vector_db_type": "chromadb",
        }
        self._save_metadata(metadata)

        result = {
            "success": True,
            "documents_processed": metadata["document_count"],
            "chunks_indexed": len(chunks),
            "duration_seconds": duration,
            "errors": errors,
        }

        if track_moves:
            result["file_moves"] = file_moves

        return result

    def get_stats(self) -> dict:
        """
        Get knowledge base statistics.

        Returns:
            Dictionary with stats and breakdowns.
        """
        # Load rebuild metadata
        metadata = self._load_metadata()

        # Get collection stats
        try:
            collection_count = self.collection.count()
        except Exception:
            collection_count = 0

        # Get all metadata for grouping
        try:
            all_data = self.collection.get(include=["metadatas"])
            metadatas = all_data.get("metadatas", [])
        except Exception:
            metadatas = []

        # Compute groupings
        by_type = {}
        by_category = {}
        by_confidence = {}
        by_status = {}

        for meta in metadatas:
            # By type
            doc_type = meta.get("type", "unknown")
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

            # By category (from file path)
            file_path = meta.get("file_path", "")
            if file_path:
                parts = file_path.split("/")
                if len(parts) > 1:
                    category = parts[0]
                    by_category[category] = by_category.get(category, 0) + 1

            # By confidence
            confidence = meta.get("confidence", "unknown")
            by_confidence[confidence] = by_confidence.get(confidence, 0) + 1

            # By status
            status = meta.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "document_count": metadata.get("document_count", 0),
            "chunk_count": collection_count,
            "by_type": by_type,
            "by_category": by_category,
            "by_confidence": by_confidence,
            "by_status": by_status,
            "index_metadata": {
                "last_rebuild": metadata.get("last_rebuild"),
                "embedding_model": metadata.get("embedding_model"),
                "embedding_dimensions": metadata.get("embedding_dimensions"),
                "vector_db_type": metadata.get("vector_db_type", "chromadb"),
            },
        }

    def _index_chunks(self, chunks: list[Chunk], verbose: bool = False, batch_size: int = 100):
        """Index chunks in batches."""
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch = chunks[i : i + batch_size]

            ids = [c.chunk_id for c in batch]
            documents = [c.text for c in batch]
            metadatas = [c.metadata for c in batch]

            # Generate embeddings
            embeddings = self.embedding_service.embed(documents)

            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )

            if verbose:
                logger.info(f"Indexed {min(i + batch_size, total)}/{total} chunks")

    def _build_where_clause(self, filters: dict) -> Optional[dict]:
        """Build ChromaDB where clause from filters."""
        conditions = []

        for key, value in filters.items():
            if value is None:
                continue

            # Map filter keys to metadata keys
            metadata_key = key
            if key in ("airline", "alliance", "cabin", "type", "confidence", "status"):
                metadata_key = key
            elif key == "route":
                metadata_key = "routes"

            conditions.append({metadata_key: {"$eq": value}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def _save_metadata(self, metadata: dict):
        """Save rebuild metadata to file."""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def _load_metadata(self) -> dict:
        """Load rebuild metadata from file."""
        if not self.metadata_file.exists():
            return {}
        try:
            with open(self.metadata_file) as f:
                return json.load(f)
        except Exception:
            return {}
