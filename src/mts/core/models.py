"""Small data objects shared by the core and its callers."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class TransformationRequest:
    """Metadata is UTF-8 text; schema IDs identify explicit catalog versions."""

    metadata: str
    source_schema: str
    target_schema: str
    input_format: str = "xml"
    output_format: str = "xml"
    crosswalk_id: str | None = None


@dataclass(frozen=True)
class Crosswalk:
    """XML-to-XML schema mapping; client formats are derived from converters."""

    id: str
    version: str
    source_schema: str
    target_schema: str
    # Fixed execution convention, excluded from catalog fields and discovery.
    input_format: ClassVar[str] = "xml"
    output_format: ClassVar[str] = "xml"
    path: Path
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Converter:
    """Change serialization within one schema using a trusted local resource."""

    id: str
    version: str
    schema: str
    input_format: str
    output_format: str
    path: Path
    notes: tuple[str, ...] = ()


@dataclass
class TransformationResult:
    """Serialized metadata and a machine-readable transformation report."""

    metadata: str
    media_type: str
    report: dict = field(default_factory=dict)
