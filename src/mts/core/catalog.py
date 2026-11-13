"""Local catalog discovery and deterministic crosswalk selection."""

import json
from pathlib import Path

from .exceptions import TransformationError
from .models import Converter, Crosswalk


class Catalog:
    """Load trusted operator resources; never accept a client-supplied file path."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        data = json.loads((self.root / "catalog.json").read_text())
        self.schemas = {item["id"]: item for item in data["schemas"]}
        if len(self.schemas) != len(data["schemas"]):
            raise ValueError("Duplicate schema IDs")
        self.crosswalks = []
        for entry in data["crosswalks"]:
            item = dict(entry)
            item["path"] = self.local_path(item["path"])
            item["notes"] = tuple(item.get("notes", []))
            crosswalk = Crosswalk(**item)
            for schema_id, fmt in [
                (crosswalk.source_schema, crosswalk.input_format),
                (crosswalk.target_schema, crosswalk.output_format),
            ]:
                if fmt not in self.schemas[schema_id]["formats"]:
                    raise ValueError(f"Unknown representation: {schema_id}/{fmt}")
            self.crosswalks.append(crosswalk)
        if len({c.id for c in self.crosswalks}) != len(self.crosswalks):
            raise ValueError("Crosswalk IDs must be unique, including across versions")

        self.converters = []
        for entry in data.get("converters", []):
            item = dict(entry)
            item["path"] = self.local_path(item["path"])
            item["notes"] = tuple(item.get("notes", []))
            converter = Converter(**item)
            for fmt in (converter.input_format, converter.output_format):
                if fmt not in self.schemas[converter.schema]["formats"]:
                    raise ValueError(f"Unknown converter representation: {fmt}")
            self.converters.append(converter)
        keys = [(c.schema, c.input_format, c.output_format) for c in self.converters]
        if len(set(keys)) != len(keys):
            raise ValueError("Configure one converter per schema/format pair")
        ids = [c.id for c in self.crosswalks + self.converters]
        if len(set(ids)) != len(ids):
            raise ValueError("Crosswalk and converter IDs must be unique")

    def local_path(self, filename):
        """Resolve an existing resource beneath the configured root."""
        path = (self.root / filename).resolve()
        if not path.is_relative_to(self.root) or not path.is_file():
            raise ValueError(f"Invalid resource path: {filename}")
        return path

    def validate_request(self, request):
        """Check declared schema representations before selecting operations."""
        for schema_id, fmt in [
            (request.source_schema, request.input_format),
            (request.target_schema, request.output_format),
        ]:
            if schema_id not in self.schemas:
                raise TransformationError(
                    "unknown_schema", f"Unknown schema: {schema_id}"
                )
            if fmt not in self.schemas[schema_id]["formats"]:
                raise TransformationError(
                    "unsupported_format", f"Unsupported: {schema_id}/{fmt}"
                )

    def select(self, request):
        """Select by schema pair and optional ID, independently of API formats."""
        self.validate_request(request)
        matches = [
            c
            for c in self.crosswalks
            if (c.source_schema, c.target_schema)
            == (request.source_schema, request.target_schema)
            and (request.crosswalk_id is None or c.id == request.crosswalk_id)
        ]
        if not matches:
            raise TransformationError("no_crosswalk", "No matching crosswalk")
        if len(matches) > 1:
            raise TransformationError("ambiguous_crosswalk", "Specify a crosswalk_id")
        return matches[0]

    def converter(self, schema, input_format, output_format):
        """Find one direct conversion; equal formats require no operation."""
        if input_format == output_format:
            return None
        for converter in self.converters:
            if (converter.schema, converter.input_format, converter.output_format) == (
                schema,
                input_format,
                output_format,
            ):
                return converter
        raise TransformationError(
            "no_converter",
            f"No converter for {schema}: {input_format} -> {output_format}",
            stage="conversion_selection",
        )

    def supported_formats(self, crosswalk):
        """Derive client formats from schema representations and direct converters."""
        source_formats = self.schemas[crosswalk.source_schema]["formats"]
        target_formats = self.schemas[crosswalk.target_schema]["formats"]
        inputs = {"xml"}
        outputs = {"xml"}
        for converter in self.converters:
            if (
                converter.schema == crosswalk.source_schema
                and converter.output_format == "xml"
            ):
                inputs.add(converter.input_format)
            if (
                converter.schema == crosswalk.target_schema
                and converter.input_format == "xml"
            ):
                outputs.add(converter.output_format)
        return {
            "supported_input_formats": sorted(inputs.intersection(source_formats)),
            "supported_output_formats": sorted(outputs.intersection(target_formats)),
        }
