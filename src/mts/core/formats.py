"""Small registry entries for serialization formats and their validators.

A new format supplies a media type and a function that compiles its schema into
an ordinary validation callable. Crosswalk execution remains the engine's job.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator
from lxml import etree

from .xml import parse_xml


@dataclass(frozen=True)
class Format:
    """A format definition; validators return None or raise ValueError."""

    media_type: str
    compile_schema: Callable[[Path], Callable[[str], None]]


def compile_xml_schema(path: Path) -> Callable[[str], None]:
    """Compile a locally managed XSD and return its content validator."""
    parser = etree.XMLParser(no_network=True, resolve_entities=False)
    schema = etree.XMLSchema(etree.parse(str(path), parser))

    def validate(content: str) -> None:
        try:
            schema.assertValid(parse_xml(content))
        except etree.DocumentInvalid as exc:
            raise ValueError(str(exc)) from exc

    return validate


def compile_json_schema(path: Path) -> Callable[[str], None]:
    """Compile a local Draft 2020-12 schema and return its content validator."""
    definition = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(definition)
    schema = Draft202012Validator(definition)

    def reject_constant(value: str):
        raise ValueError(f"Invalid JSON constant: {value}")

    def validate(content: str) -> None:
        document = json.loads(content, parse_constant=reject_constant)
        errors = sorted(schema.iter_errors(document), key=lambda error: str(error.path))
        if errors:
            raise ValueError(errors[0].message)

    return validate


def default_formats() -> dict[str, Format]:
    """Return fresh built-in registrations, which deployments may extend."""
    return {
        "xml": Format("application/xml", compile_xml_schema),
        "json": Format("application/json", compile_json_schema),
    }
