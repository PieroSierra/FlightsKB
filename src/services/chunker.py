"""Deterministic chunker for knowledge documents."""

import logging
import re
from pathlib import Path
from typing import Optional

from src.models.chunk import Chunk
from src.models.document import Document

logger = logging.getLogger(__name__)


class ChunkerError(Exception):
    """Error during document chunking."""

    pass


class Chunker:
    """Deterministic chunker that splits documents into searchable cards."""

    def chunk_document(self, doc: Document) -> list[Chunk]:
        """
        Split a document into chunks based on ## headings.

        Each ## section becomes one chunk. Deterministic: same input
        always produces same chunk_ids and text.
        """
        chunks = []
        doc_metadata = doc.get_metadata_dict()
        file_path = str(doc.file_path) if doc.file_path else None

        # Split content by ## headings
        sections = self._split_by_headings(doc.content)

        for heading, content in sections:
            if not content.strip():
                continue

            chunk = Chunk.from_section(
                kb_id=doc.kb_id,
                heading=heading,
                content=content,
                doc_metadata=doc_metadata,
                file_path=file_path,
            )
            chunks.append(chunk)

        return chunks

    def chunk_file(self, file_path: Path) -> list[Chunk]:
        """
        Parse and chunk a single file.

        Returns empty list and logs warning if file has invalid frontmatter.
        """
        try:
            doc = Document.from_file(file_path)
            return self.chunk_document(doc)
        except KeyError as e:
            logger.warning(f"Missing required frontmatter field in {file_path}: {e}")
            return []
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return []

    def chunk_directory(
        self, directory: Path, recursive: bool = True
    ) -> tuple[list[Chunk], list[str]]:
        """
        Chunk all markdown files in a directory.

        Returns (chunks, errors) tuple.
        """
        chunks = []
        errors = []

        pattern = "**/*.md" if recursive else "*.md"
        for file_path in directory.glob(pattern):
            try:
                file_chunks = self.chunk_file(file_path)
                chunks.extend(file_chunks)
            except Exception as e:
                error_msg = f"{file_path}: {e}"
                errors.append(error_msg)
                logger.warning(f"Error processing {error_msg}")

        return chunks, errors

    def _split_by_headings(self, content: str) -> list[tuple[str, str]]:
        """
        Split markdown content by ## headings.

        Returns list of (heading, content) tuples.
        """
        sections = []

        # Pattern to match ## headings
        pattern = r"^##\s+(.+?)$"
        lines = content.split("\n")

        current_heading = None
        current_content = []

        for line in lines:
            match = re.match(pattern, line)
            if match:
                # Save previous section
                if current_heading is not None:
                    sections.append((current_heading, "\n".join(current_content)))

                # Start new section
                current_heading = match.group(1).strip()
                current_content = [line]
            elif current_heading is not None:
                current_content.append(line)

        # Save last section
        if current_heading is not None:
            sections.append((current_heading, "\n".join(current_content)))

        return sections


def get_relative_path(file_path: Path, knowledge_dir: Path) -> Optional[str]:
    """Get path relative to knowledge directory."""
    try:
        return str(file_path.relative_to(knowledge_dir))
    except ValueError:
        return str(file_path)
