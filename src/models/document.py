"""Document model with frontmatter parsing."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional

import frontmatter


class Status(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    DEPRECATED = "deprecated"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceKind(str, Enum):
    INTERNAL = "internal"
    UGC = "ugc"
    MARKETING = "marketing"
    PRESS = "press"
    BLOG = "blog"
    FORUM = "forum"
    OTHER = "other"


@dataclass
class Source:
    """Provenance information for a document."""

    kind: SourceKind
    name: str
    url: Optional[str] = None
    retrieved: Optional[date] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        """Parse source from frontmatter dict."""
        return cls(
            kind=SourceKind(data.get("kind", "other")),
            name=data.get("name", "unknown"),
            url=data.get("url"),
            retrieved=_parse_date(data.get("retrieved")),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        result = {"kind": self.kind.value, "name": self.name}
        if self.url:
            result["url"] = self.url
        if self.retrieved:
            result["retrieved"] = self.retrieved.isoformat()
        return result


@dataclass
class Entities:
    """Structured entity references."""

    airline: Optional[str] = None
    alliance: Optional[str] = None
    airports: list[str] = field(default_factory=list)
    routes: list[str] = field(default_factory=list)
    cabins: list[str] = field(default_factory=list)
    aircraft: list[str] = field(default_factory=list)
    flight_numbers: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Entities":
        """Parse entities from frontmatter dict."""
        if not data:
            return cls()
        return cls(
            airline=data.get("airline"),
            alliance=data.get("alliance"),
            airports=data.get("airports", []),
            routes=data.get("routes", []),
            cabins=data.get("cabins", []),
            aircraft=data.get("aircraft", []),
            flight_numbers=data.get("flight_numbers", []),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        result = {}
        if self.airline:
            result["airline"] = self.airline
        if self.alliance:
            result["alliance"] = self.alliance
        if self.airports:
            result["airports"] = self.airports
        if self.routes:
            result["routes"] = self.routes
        if self.cabins:
            result["cabins"] = self.cabins
        if self.aircraft:
            result["aircraft"] = self.aircraft
        if self.flight_numbers:
            result["flight_numbers"] = self.flight_numbers
        return result


@dataclass
class License:
    """Reuse permissions."""

    reuse: str = "unknown"  # ok, restricted, unknown
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "License":
        """Parse license from frontmatter dict."""
        if not data:
            return cls()
        return cls(
            reuse=data.get("reuse", "unknown"),
            notes=data.get("notes"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        result = {"reuse": self.reuse}
        if self.notes:
            result["notes"] = self.notes
        return result


@dataclass
class Document:
    """A knowledge document with frontmatter metadata."""

    kb_id: str
    type: str
    title: str
    created: date
    updated: date
    status: Status
    source: Source
    confidence: Confidence
    content: str
    file_path: Optional[Path] = None

    # Optional fields
    tags: list[str] = field(default_factory=list)
    entities: Optional[Entities] = None
    temporal_from: Optional[date] = None
    temporal_to: Optional[date] = None
    geo_regions: list[str] = field(default_factory=list)
    audience: Optional[str] = None
    license: Optional[License] = None

    @classmethod
    def from_file(cls, file_path: Path) -> "Document":
        """Parse a document from a Markdown file."""
        post = frontmatter.load(file_path)
        metadata = post.metadata

        return cls(
            kb_id=metadata["kb_id"],
            type=metadata["type"],
            title=metadata["title"],
            created=_parse_date(metadata["created"]),
            updated=_parse_date(metadata["updated"]),
            status=Status(metadata.get("status", "draft")),
            source=Source.from_dict(metadata.get("source", {})),
            confidence=Confidence(metadata.get("confidence", "medium")),
            content=post.content,
            file_path=file_path,
            tags=metadata.get("tags", []),
            entities=Entities.from_dict(metadata.get("entities")),
            temporal_from=_parse_date(metadata.get("temporal", {}).get("effective_from")),
            temporal_to=_parse_date(metadata.get("temporal", {}).get("effective_to")),
            geo_regions=metadata.get("geo", {}).get("regions", []),
            audience=metadata.get("audience"),
            license=License.from_dict(metadata.get("license")),
        )

    @classmethod
    def from_string(cls, content: str, file_path: Optional[Path] = None) -> "Document":
        """Parse a document from a Markdown string."""
        post = frontmatter.loads(content)
        metadata = post.metadata

        return cls(
            kb_id=metadata["kb_id"],
            type=metadata["type"],
            title=metadata["title"],
            created=_parse_date(metadata["created"]),
            updated=_parse_date(metadata["updated"]),
            status=Status(metadata.get("status", "draft")),
            source=Source.from_dict(metadata.get("source", {})),
            confidence=Confidence(metadata.get("confidence", "medium")),
            content=post.content,
            file_path=file_path,
            tags=metadata.get("tags", []),
            entities=Entities.from_dict(metadata.get("entities")),
            temporal_from=_parse_date(metadata.get("temporal", {}).get("effective_from")),
            temporal_to=_parse_date(metadata.get("temporal", {}).get("effective_to")),
            geo_regions=metadata.get("geo", {}).get("regions", []),
            audience=metadata.get("audience"),
            license=License.from_dict(metadata.get("license")),
        )

    def to_markdown(self) -> str:
        """Convert document to Markdown string with frontmatter."""
        metadata = {
            "kb_id": self.kb_id,
            "type": self.type,
            "title": self.title,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "status": self.status.value,
            "source": self.source.to_dict(),
            "confidence": self.confidence.value,
        }

        if self.tags:
            metadata["tags"] = self.tags
        if self.entities:
            entities_dict = self.entities.to_dict()
            if entities_dict:
                metadata["entities"] = entities_dict
        if self.temporal_from or self.temporal_to:
            temporal = {}
            if self.temporal_from:
                temporal["effective_from"] = self.temporal_from.isoformat()
            if self.temporal_to:
                temporal["effective_to"] = self.temporal_to.isoformat()
            metadata["temporal"] = temporal
        if self.geo_regions:
            metadata["geo"] = {"regions": self.geo_regions}
        if self.audience:
            metadata["audience"] = self.audience
        if self.license:
            metadata["license"] = self.license.to_dict()

        post = frontmatter.Post(self.content, **metadata)
        return frontmatter.dumps(post)

    def get_metadata_dict(self) -> dict:
        """Get flat metadata dictionary for ChromaDB."""
        metadata = {
            "kb_id": self.kb_id,
            "type": self.type,
            "title": self.title,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "source_kind": self.source.kind.value,
        }

        if self.file_path:
            metadata["file_path"] = str(self.file_path)
        if self.entities:
            if self.entities.airline:
                metadata["airline"] = self.entities.airline
            if self.entities.alliance:
                metadata["alliance"] = self.entities.alliance
            if self.entities.airports:
                metadata["airports"] = ",".join(self.entities.airports)
            if self.entities.routes:
                metadata["routes"] = ",".join(self.entities.routes)
            if self.entities.cabins:
                metadata["cabins"] = ",".join(self.entities.cabins)
        if self.geo_regions:
            metadata["regions"] = ",".join(self.geo_regions)

        return metadata


def _parse_date(value) -> Optional[date]:
    """Parse a date from various formats."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    return None
