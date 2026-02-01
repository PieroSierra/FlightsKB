"""Ingestion service for adding new knowledge."""

import re
import uuid
from datetime import date
from pathlib import Path
from typing import Optional

import frontmatter


class IngestService:
    """Service for ingesting new content into the knowledge base."""

    def __init__(self, knowledge_dir: Path):
        """
        Initialize the ingest service.

        Args:
            knowledge_dir: Path to knowledge directory.
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.inbox_dir = self.knowledge_dir / "inbox"
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def ingest_text(
        self,
        text: str,
        source_kind: str = "internal",
        source_name: str = "manual",
        title: Optional[str] = None,
        category: str = "inbox",
        confidence: str = "medium",
    ) -> dict:
        """
        Ingest raw text content.

        All files are saved to inbox/ as a staging area with destination_category
        in frontmatter. During rebuild, files are moved to their destination.

        Args:
            text: Raw text to ingest.
            source_kind: Source category.
            source_name: Source name/author.
            title: Optional title (auto-generated if not provided).
            category: Destination category (where to move on rebuild).
            confidence: Confidence level (high, medium, low).

        Returns:
            Dictionary with ingestion result.
        """
        # Generate kb_id
        kb_id = f"ingest-{uuid.uuid4().hex[:8]}"

        # Auto-generate title from first line or text preview
        if not title:
            first_line = text.split("\n")[0].strip()
            title = first_line[:60] if first_line else f"Ingested {date.today().isoformat()}"

        # Split into cards using heuristic chunking
        cards = self._heuristic_chunk(text)

        # Generate markdown content
        content = "\n\n".join(cards)

        # Create frontmatter - always save to inbox with destination_category
        metadata = {
            "kb_id": kb_id,
            "type": "ingested",
            "title": title,
            "created": date.today().isoformat(),
            "updated": date.today().isoformat(),
            "status": "draft",
            "source": {
                "kind": source_kind,
                "name": source_name,
                "url": None,
                "retrieved": None,
            },
            "confidence": confidence,
            "destination_category": category,  # Tag with where to move on rebuild
        }

        # Always save to inbox (staging area)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create post and save
        post = frontmatter.Post(content, **metadata)
        output_file = self.inbox_dir / f"{kb_id}.md"
        with open(output_file, "w") as f:
            f.write(frontmatter.dumps(post))

        return {
            "kb_id": kb_id,
            "output_file": str(output_file),
            "file_path": str(output_file),
            "card_count": len(cards),
            "chunk_count": len(cards),
            "title": title,
        }

    def ingest_txt(
        self,
        content_bytes: bytes,
        source_kind: str = "internal",
        title: Optional[str] = None,
        category: str = "inbox",
        confidence: str = "medium",
    ) -> dict:
        """Ingest a .txt file from bytes."""
        text = content_bytes.decode("utf-8")
        return self.ingest_text(
            text=text,
            source_kind=source_kind,
            source_name="file",
            title=title,
            category=category,
            confidence=confidence,
        )

    def ingest_pdf(
        self,
        content_bytes: bytes,
        source_kind: str = "internal",
        title: Optional[str] = None,
        category: str = "inbox",
        confidence: str = "medium",
    ) -> dict:
        """Ingest a PDF file from bytes."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF required for PDF ingestion. Run: pip install pymupdf")

        doc = fitz.open(stream=content_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        text = "\n\n".join(text_parts)

        return self.ingest_text(
            text=text,
            source_kind=source_kind,
            source_name="file",
            title=title,
            category=category,
            confidence=confidence,
        )

    def ingest_html(
        self,
        content_bytes: bytes,
        source_kind: str = "internal",
        title: Optional[str] = None,
        category: str = "inbox",
        confidence: str = "medium",
    ) -> dict:
        """Ingest an HTML file from bytes."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("BeautifulSoup required for HTML ingestion. Run: pip install beautifulsoup4")

        soup = BeautifulSoup(content_bytes.decode("utf-8"), "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)

        return self.ingest_text(
            text=text,
            source_kind=source_kind,
            source_name="file",
            title=title,
            category=category,
            confidence=confidence,
        )

    def ingest_file(
        self,
        file_path: Path,
        source_kind: str = "internal",
        source_name: str = "file",
        title: Optional[str] = None,
    ) -> dict:
        """
        Ingest a file.

        Args:
            file_path: Path to file to ingest.
            source_kind: Source category.
            source_name: Source name/author.
            title: Optional title.

        Returns:
            Dictionary with ingestion result.
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        # Extract text based on file type
        if suffix == ".md":
            text = self._extract_markdown(file_path)
        elif suffix == ".txt":
            text = self._extract_text(file_path)
        elif suffix == ".pdf":
            text = self._extract_pdf(file_path)
        elif suffix in (".html", ".htm"):
            text = self._extract_html(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        # Use filename as title if not provided
        if not title:
            title = file_path.stem

        return self.ingest_text(
            text=text,
            source_kind=source_kind,
            source_name=source_name,
            title=title,
        )

    def _extract_markdown(self, file_path: Path) -> str:
        """Extract content from markdown file."""
        with open(file_path) as f:
            content = f.read()

        # If it has frontmatter, extract just the content
        try:
            post = frontmatter.loads(content)
            return post.content
        except Exception:
            return content

    def _extract_text(self, file_path: Path) -> str:
        """Extract content from text file."""
        with open(file_path) as f:
            return f.read()

    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("PyMuPDF required for PDF ingestion. Run: pip install pymupdf")

        doc = fitz.open(file_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n\n".join(text_parts)

    def _extract_html(self, file_path: Path) -> str:
        """Extract text from HTML file."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("BeautifulSoup required for HTML ingestion. Run: pip install beautifulsoup4")

        with open(file_path) as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        return soup.get_text(separator="\n", strip=True)

    def _heuristic_chunk(self, text: str) -> list[str]:
        """
        Split text into card sections using heuristics.

        Tries to identify natural section boundaries.
        """
        # If text already has ## headers, use those
        if re.search(r"^##\s+", text, re.MULTILINE):
            return self._split_existing_headers(text)

        # Otherwise, split by double newlines into paragraphs
        paragraphs = re.split(r"\n\n+", text.strip())

        # Group paragraphs into cards (aim for ~3-5 paragraphs per card)
        cards = []
        current_card = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            current_card.append(para)
            current_length += len(para)

            # Create new card if we have enough content
            if current_length > 500 or len(current_card) >= 4:
                card_num = len(cards) + 1
                card_content = f"## Section {card_num}\n\n" + "\n\n".join(current_card)
                cards.append(card_content)
                current_card = []
                current_length = 0

        # Add remaining content
        if current_card:
            card_num = len(cards) + 1
            card_content = f"## Section {card_num}\n\n" + "\n\n".join(current_card)
            cards.append(card_content)

        # If no cards created, create one from all text
        if not cards:
            cards.append(f"## Content\n\n{text}")

        return cards

    def _split_existing_headers(self, text: str) -> list[str]:
        """Split text that already has ## headers."""
        cards = []
        current_card = []

        for line in text.split("\n"):
            if line.startswith("## ") and current_card:
                cards.append("\n".join(current_card))
                current_card = []
            current_card.append(line)

        if current_card:
            cards.append("\n".join(current_card))

        return cards
