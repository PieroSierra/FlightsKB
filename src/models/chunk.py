"""Chunk (Card) model for searchable knowledge sections."""

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ClaimType(str, Enum):
    FACT = "fact"
    EVALUATION = "evaluation"
    TACTIC = "tactic"
    RULE_OF_THUMB = "rule_of_thumb"
    WARNING = "warning"
    COMPARISON = "comparison"


@dataclass
class AppliesTo:
    """Parsed selector DSL from 'Applies to:' field."""

    airline: Optional[str] = None
    airports: list[str] = field(default_factory=list)
    routes: list[str] = field(default_factory=list)
    cabin: Optional[str] = None
    aircraft: Optional[str] = None
    flight: Optional[str] = None
    alliance: Optional[str] = None
    region: Optional[str] = None

    @classmethod
    def parse(cls, text: str) -> "AppliesTo":
        """Parse applies-to DSL string like 'airline=BA, routes=LHR-JFK'."""
        result = cls()
        if not text:
            return result

        # Split by comma and parse key=value pairs
        for part in text.split(","):
            part = part.strip()
            if "=" not in part:
                continue

            key, value = part.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "airline":
                result.airline = value
            elif key == "airports":
                result.airports = [v.strip() for v in value.split(",")]
            elif key == "routes":
                result.routes = [v.strip() for v in value.split(",")]
            elif key == "cabin":
                result.cabin = value
            elif key == "aircraft":
                result.aircraft = value
            elif key == "flight":
                result.flight = value
            elif key == "alliance":
                result.alliance = value
            elif key == "region":
                result.region = value

        return result

    def to_metadata(self) -> dict:
        """Convert to flat metadata for ChromaDB."""
        metadata = {}
        if self.airline:
            metadata["applies_airline"] = self.airline
        if self.airports:
            metadata["applies_airports"] = ",".join(self.airports)
        if self.routes:
            metadata["applies_routes"] = ",".join(self.routes)
        if self.cabin:
            metadata["applies_cabin"] = self.cabin
        if self.aircraft:
            metadata["applies_aircraft"] = self.aircraft
        if self.flight:
            metadata["applies_flight"] = self.flight
        if self.alliance:
            metadata["applies_alliance"] = self.alliance
        if self.region:
            metadata["applies_region"] = self.region
        return metadata


@dataclass
class Chunk:
    """A searchable section (card) within a document."""

    chunk_id: str
    doc_id: str
    title: str
    text: str
    hash: str
    metadata: dict = field(default_factory=dict)

    # Card-level parsed fields
    claim_type: Optional[ClaimType] = None
    applies_to: Optional[AppliesTo] = None
    summary: Optional[str] = None
    structured_blob: Optional[dict] = None

    # Source reference
    file_path: Optional[str] = None

    @classmethod
    def from_section(
        cls,
        kb_id: str,
        heading: str,
        content: str,
        doc_metadata: dict,
        file_path: Optional[str] = None,
    ) -> "Chunk":
        """Create a chunk from a markdown section."""
        chunk_id = f"{kb_id}#{slugify(heading)}"
        content_hash = compute_hash(content)

        # Parse card-level fields
        claim_type = _extract_claim_type(content)
        applies_to = _extract_applies_to(content)
        summary = _extract_summary(content)
        structured_blob = _extract_json_blob(content)

        # Merge metadata
        metadata = {**doc_metadata}
        if claim_type:
            metadata["claim_type"] = claim_type.value
        if applies_to:
            metadata.update(applies_to.to_metadata())
        if file_path:
            metadata["file_path"] = file_path

        return cls(
            chunk_id=chunk_id,
            doc_id=kb_id,
            title=heading,
            text=content,
            hash=content_hash,
            metadata=metadata,
            claim_type=claim_type,
            applies_to=applies_to,
            summary=summary,
            structured_blob=structured_blob,
            file_path=file_path,
        )


def slugify(text: str) -> str:
    """Convert heading to URL-safe slug."""
    # Lowercase
    slug = text.lower()
    # Replace non-alphanumeric with dashes
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing dashes
    slug = slug.strip("-")
    return slug


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of normalized content."""
    # Normalize: strip whitespace, lowercase
    normalized = content.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _extract_claim_type(content: str) -> Optional[ClaimType]:
    """Extract claim type from card content."""
    match = re.search(r"\*\*Claim type:\*\*\s*(\w+)", content, re.IGNORECASE)
    if match:
        try:
            return ClaimType(match.group(1).lower())
        except ValueError:
            pass
    return None


def _extract_applies_to(content: str) -> Optional[AppliesTo]:
    """Extract applies-to selector from card content."""
    match = re.search(r"\*\*Applies to:\*\*\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if match:
        return AppliesTo.parse(match.group(1))
    return None


def _extract_summary(content: str) -> Optional[str]:
    """Extract summary from card content."""
    match = re.search(r"\*\*Summary:\*\*\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _extract_json_blob(content: str) -> Optional[dict]:
    """Extract JSON block from card content."""
    import json

    match = re.search(r"```json\s*\n(.+?)\n```", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None
